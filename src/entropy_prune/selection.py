"""Chunk selection under a budget.

Module 1 scores, this module chooses. Every selector has the same shape:
given a similarity matrix, an optional query-relevance vector, per-chunk
costs and a budget, return the indices that survive.

The selectors are deliberately comparable, including the baselines, because
a pruner's only meaningful claim is relative to a *tuned* alternative.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def _validate(similarity: np.ndarray, costs: Sequence[int]) -> int:
    """Check shapes agree and return the chunk count."""
    if similarity.ndim != 2 or similarity.shape[0] != similarity.shape[1]:
        raise ValueError(f"similarity must be square, got {similarity.shape}")
    if len(costs) != similarity.shape[0]:
        raise ValueError(f"{len(costs)} costs for {similarity.shape[0]} chunks")
    return similarity.shape[0]


def _fits(chosen_cost: int, item_cost: int, budget: int) -> bool:
    """Whether adding an item keeps the running cost within budget."""
    return chosen_cost + item_cost <= budget


def coverage_score(similarity: np.ndarray, kept: Sequence[int]) -> float:
    """Mean best-representation of every chunk by the kept subset.

    This is the facility-location objective: for each chunk, how well is it
    represented by its nearest survivor.

    Args:
        similarity: Symmetric ``(n, n)`` cosine matrix.
        kept: Indices of surviving chunks.

    Returns:
        Mean over all chunks of ``max_{j in kept} S[i][j]``; 0.0 if nothing kept.
    """
    if len(kept) == 0:
        return 0.0
    return float(similarity[:, np.asarray(kept, dtype=np.intp)].max(axis=1).mean())


def select_random(
    similarity: np.ndarray,
    costs: Sequence[int],
    budget: int,
    seed: int = 0,
) -> list[int]:
    """Shuffle and take until the budget is spent -- the floor baseline.

    Args:
        similarity: Symmetric ``(n, n)`` cosine matrix (shape only, unused).
        costs: Token cost per chunk.
        budget: Total token budget.
        seed: Seed for the shuffle.

    Returns:
        Sorted surviving indices.
    """
    n = _validate(similarity, costs)
    order = np.random.default_rng(seed).permutation(n)
    kept: list[int] = []
    spent = 0
    for i in order:
        if _fits(spent, costs[i], budget):
            kept.append(int(i))
            spent += costs[i]
    return sorted(kept)


def select_top_relevance(
    similarity: np.ndarray,
    costs: Sequence[int],
    budget: int,
    relevance: np.ndarray,
) -> list[int]:
    """Take the most query-relevant chunks until the budget is spent.

    The competitor that actually ships in most RAG pipelines.

    Args:
        similarity: Symmetric ``(n, n)`` cosine matrix (shape only, unused).
        costs: Token cost per chunk.
        budget: Total token budget.
        relevance: ``(n,)`` cosine similarity of each chunk to the query.

    Returns:
        Sorted surviving indices.
    """
    _validate(similarity, costs)
    kept: list[int] = []
    spent = 0
    for i in np.argsort(-relevance):
        if _fits(spent, costs[i], budget):
            kept.append(int(i))
            spent += costs[i]
    return sorted(kept)


def select_threshold(
    similarity: np.ndarray,
    costs: Sequence[int],
    budget: int,
    tau: float,
    relevance: np.ndarray | None = None,
) -> list[int]:
    """Sequential dedup: reject anything within ``tau`` of an accepted chunk.

    Args:
        similarity: Symmetric ``(n, n)`` cosine matrix.
        costs: Token cost per chunk.
        budget: Total token budget.
        tau: Reject a candidate whose similarity to any kept chunk is >= tau.
        relevance: Optional ``(n,)`` query relevance setting the scan order;
            ``None`` scans in corpus order.

    Returns:
        Sorted surviving indices.
    """
    _validate(similarity, costs)
    order = range(len(costs)) if relevance is None else np.argsort(-relevance)
    kept: list[int] = []
    spent = 0
    for i in order:
        if not _fits(spent, costs[i], budget):
            continue
        if all(similarity[i, j] < tau for j in kept):
            kept.append(int(i))
            spent += costs[i]
    return sorted(kept)


def select_greedy_coverage(
    similarity: np.ndarray,
    costs: Sequence[int],
    budget: int,
    cost_weighted: bool = True,
) -> list[int]:
    """Greedy facility location under a knapsack budget.

    Monotone submodular, so plain greedy is a ``1 - 1/e`` approximation under a
    cardinality constraint. A token budget is a knapsack constraint, which
    breaks that bound; ranking by gain-per-token restores a comparable one,
    which is what ``cost_weighted`` does.

    Args:
        similarity: Symmetric ``(n, n)`` cosine matrix.
        costs: Token cost per chunk.
        budget: Total token budget.
        cost_weighted: Rank candidates by marginal gain divided by token cost
            rather than by marginal gain alone.

    Returns:
        Sorted surviving indices.
    """
    n = _validate(similarity, costs)
    best = np.full(n, -np.inf, dtype=np.float64)
    kept: list[int] = []
    spent = 0
    remaining = set(range(n))

    while remaining:
        winner, winner_gain = -1, -np.inf
        current = best_sum(best)  # constant across candidates; hoisted out
        for c in remaining:
            if not _fits(spent, costs[c], budget):
                continue
            gain = float(np.maximum(best, similarity[:, c]).sum()) - current
            score = gain / costs[c] if cost_weighted else gain
            if score > winner_gain:
                winner, winner_gain = c, score
        if winner < 0:
            break
        kept.append(winner)
        spent += costs[winner]
        best = np.maximum(best, similarity[:, winner])
        remaining.discard(winner)
    return sorted(kept)


def best_sum(best: np.ndarray) -> float:
    """Sum of a running-best array, treating the -inf start state as zero."""
    finite = best[np.isfinite(best)]
    return float(finite.sum()) if finite.size else 0.0


def select_mmr(
    similarity: np.ndarray,
    costs: Sequence[int],
    budget: int,
    relevance: np.ndarray,
    lambda_: float = 0.7,
) -> list[int]:
    """Maximal Marginal Relevance: interpolate relevance against redundancy.

    Args:
        similarity: Symmetric ``(n, n)`` cosine matrix.
        costs: Token cost per chunk.
        budget: Total token budget.
        relevance: ``(n,)`` cosine similarity of each chunk to the query.
        lambda_: 1.0 is pure relevance, 0.0 is pure diversity.

    Returns:
        Sorted surviving indices.
    """
    n = _validate(similarity, costs)
    kept: list[int] = []
    spent = 0
    max_sim = np.zeros(n, dtype=np.float64)
    remaining = set(range(n))

    while remaining:
        winner, winner_score = -1, -np.inf
        for c in remaining:
            if not _fits(spent, costs[c], budget):
                continue
            score = lambda_ * relevance[c] - (1.0 - lambda_) * max_sim[c]
            if score > winner_score:
                winner, winner_score = c, score
        if winner < 0:
            break
        kept.append(winner)
        spent += costs[winner]
        max_sim = np.maximum(max_sim, similarity[:, winner])
        remaining.discard(winner)
    return sorted(kept)
