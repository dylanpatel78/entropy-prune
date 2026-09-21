"""Tests for the selection engine (Module 4)."""

from __future__ import annotations

import numpy as np
import pytest

from entropy_prune.embeddings import l2_normalize
from entropy_prune.selection import (
    coverage_score,
    select_greedy_coverage,
    select_mmr,
    select_random,
    select_threshold,
    select_top_relevance,
)
from entropy_prune.similarity import cosine_similarity_matrix

Toy = tuple[np.ndarray, list[int], np.ndarray]


@pytest.fixture
def toy() -> Toy:
    """Two near-duplicates, two distinct chunks, uniform cost."""
    vectors = l2_normalize(
        np.array(
            [[1.0, 0.0, 0.0], [0.99, 0.1, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
    )
    return (
        cosine_similarity_matrix(vectors),
        [1, 1, 1, 1],
        np.array([0.9, 0.8, 0.1, 0.0]),
    )


def test_every_selector_respects_the_budget(toy: Toy) -> None:
    sim, costs, rel = toy
    budget = 2
    for kept in (
        select_random(sim, costs, budget, seed=3),
        select_top_relevance(sim, costs, budget, rel),
        select_threshold(sim, costs, budget, 0.5),
        select_greedy_coverage(sim, costs, budget),
        select_mmr(sim, costs, budget, rel, lambda_=0.7),
    ):
        assert sum(costs[i] for i in kept) <= budget
        assert len(set(kept)) == len(kept)
        assert all(0 <= i < len(costs) for i in kept)


def test_variable_costs_are_honoured() -> None:
    sim = np.eye(4, dtype=np.float32)
    costs = [10, 1, 1, 1]
    kept = select_greedy_coverage(sim, costs, budget=3)
    assert 0 not in kept, "a chunk costing more than the budget must be skipped"
    assert sum(costs[i] for i in kept) <= 3


def test_greedy_prefers_distinct_chunks_over_duplicates(toy: Toy) -> None:
    sim, costs, _ = toy
    kept = select_greedy_coverage(sim, costs, budget=2)
    # chunks 0 and 1 are near-identical; a coverage objective should not take both
    assert not {0, 1}.issubset(set(kept))


def test_coverage_increases_with_budget(toy: Toy) -> None:
    sim, costs, _ = toy
    scores = [
        coverage_score(sim, select_greedy_coverage(sim, costs, b)) for b in (1, 2, 3, 4)
    ]
    assert scores == sorted(scores), "coverage must be monotone in the budget"
    assert scores[-1] == pytest.approx(1.0, abs=1e-6), (
        "keeping everything covers everything"
    )


def test_mmr_lambda_one_matches_pure_relevance(toy: Toy) -> None:
    sim, costs, rel = toy
    assert select_mmr(sim, costs, 2, rel, lambda_=1.0) == select_top_relevance(
        sim, costs, 2, rel
    )


def test_mmr_lambda_zero_ignores_relevance(toy: Toy) -> None:
    sim, costs, rel = toy
    diverse = select_mmr(sim, costs, 2, rel, lambda_=0.0)
    relevant = select_mmr(sim, costs, 2, rel, lambda_=1.0)
    assert diverse != relevant, "the lambda knob must actually change the outcome"


def test_threshold_rejects_near_duplicates(toy: Toy) -> None:
    sim, costs, _ = toy
    kept = select_threshold(sim, costs, budget=4, tau=0.5)
    assert not {0, 1}.issubset(set(kept))


def test_random_is_reproducible(toy: Toy) -> None:
    sim, costs, _ = toy
    assert select_random(sim, costs, 2, seed=7) == select_random(sim, costs, 2, seed=7)


def test_empty_selection_scores_zero(toy: Toy) -> None:
    sim, _, _ = toy
    assert coverage_score(sim, []) == 0.0
