"""Measuring whether pruning keeps the information the task needs.

The pruner's own objectives -- coverage and effective rank -- are what the
selector maximises, so scoring against them is circular. These metrics use
external ground truth instead: the sentences a benchmark says are required to
answer the question.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class PruneResult:
    """Outcome of one selector on one question.

    Attributes:
        kept: Surviving chunk indices.
        support_recall: Fraction of required sentences that survived.
        fully_supported: Whether every required sentence survived.
        kept_tokens: Token cost of the surviving chunks.
        total_tokens: Token cost before pruning.
    """

    kept: tuple[int, ...]
    support_recall: float
    fully_supported: bool
    kept_tokens: int
    total_tokens: int

    @property
    def compression(self) -> float:
        """Fraction of tokens removed, in ``[0, 1]``."""
        if self.total_tokens == 0:
            return 0.0
        return 1.0 - self.kept_tokens / self.total_tokens


def score_selection(
    kept: Sequence[int],
    gold: Sequence[int],
    costs: Sequence[int],
) -> PruneResult:
    """Score one selection against the benchmark's required sentences.

    Args:
        kept: Surviving chunk indices.
        gold: Indices of the sentences the benchmark marks as required.
        costs: Token cost per chunk.

    Returns:
        A :class:`PruneResult` holding recall, support and token counts.
    """
    kept_set = set(int(i) for i in kept)
    gold_set = set(int(i) for i in gold)
    hit = len(kept_set & gold_set)
    recall = hit / len(gold_set) if gold_set else 1.0
    return PruneResult(
        kept=tuple(sorted(kept_set)),
        support_recall=recall,
        fully_supported=bool(gold_set) and hit == len(gold_set),
        kept_tokens=sum(costs[i] for i in kept_set),
        total_tokens=sum(costs),
    )


def aggregate(results: Sequence[PruneResult]) -> dict[str, float]:
    """Average a selector's per-question results into reportable figures.

    Args:
        results: One :class:`PruneResult` per question.

    Returns:
        Mean support recall, full-support rate, compression, and the count.
    """
    if not results:
        return {"support_recall": 0.0, "full_support": 0.0, "compression": 0.0, "n": 0}
    return {
        "support_recall": float(np.mean([r.support_recall for r in results])),
        "full_support": float(np.mean([r.fully_supported for r in results])),
        "compression": float(np.mean([r.compression for r in results])),
        "n": len(results),
    }


def wilson_interval(
    successes: int, trials: int, z: float = 1.96
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Preferred over the normal approximation because full-support rates sit
    close to 1.0, where the normal interval overshoots past 100%.

    Args:
        successes: Number of successes.
        trials: Number of trials.
        z: Standard-normal quantile; 1.96 gives a 95% interval.

    Returns:
        Lower and upper bounds, each clamped to ``[0, 1]``.
    """
    if trials == 0:
        return (0.0, 0.0)
    phat = successes / trials
    denom = 1.0 + z * z / trials
    center = (phat + z * z / (2 * trials)) / denom
    margin = z * np.sqrt(phat * (1 - phat) / trials + z * z / (4 * trials * trials))
    margin /= denom
    return (max(0.0, center - margin), min(1.0, center + margin))
