"""Tests for the evaluation harness (Module 6)."""

from __future__ import annotations

import pytest

from entropy_prune.evaluation import aggregate, score_selection, wilson_interval


def test_scores_perfect_and_total_miss() -> None:
    costs = [5, 5, 5, 5]
    perfect = score_selection(kept=[0, 1], gold=[0, 1], costs=costs)
    assert perfect.support_recall == 1.0
    assert perfect.fully_supported
    assert perfect.compression == pytest.approx(0.5)

    missed = score_selection(kept=[2, 3], gold=[0, 1], costs=costs)
    assert missed.support_recall == 0.0
    assert not missed.fully_supported


def test_partial_support_is_not_full_support() -> None:
    result = score_selection(kept=[0], gold=[0, 1], costs=[1, 1, 1])
    assert result.support_recall == pytest.approx(0.5)
    assert not result.fully_supported, "half the evidence is not full support"


def test_compression_uses_token_cost_not_chunk_count() -> None:
    # keeping 1 of 2 chunks is 50% of chunks but only 10% of tokens
    result = score_selection(kept=[0], gold=[0], costs=[10, 90])
    assert result.compression == pytest.approx(0.9)


def test_aggregate_averages_and_handles_empty() -> None:
    costs = [1, 1]
    rows = [
        score_selection([0], [0], costs),  # recall 1.0
        score_selection([1], [0], costs),  # recall 0.0
    ]
    agg = aggregate(rows)
    assert agg["support_recall"] == pytest.approx(0.5)
    assert agg["full_support"] == pytest.approx(0.5)
    assert agg["n"] == 2
    assert aggregate([])["n"] == 0


def test_wilson_interval_brackets_the_estimate_and_stays_in_range() -> None:
    lo, hi = wilson_interval(45, 50)
    assert 0.0 <= lo < 0.9 < hi <= 1.0, "interval must bracket p-hat and stay in [0,1]"
    # a perfect run must not produce an upper bound above 1
    lo2, hi2 = wilson_interval(50, 50)
    assert hi2 == pytest.approx(1.0)
    assert lo2 < 1.0
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_wider_interval_with_less_data() -> None:
    narrow = wilson_interval(900, 1000)
    wide = wilson_interval(9, 10)
    assert (wide[1] - wide[0]) > (narrow[1] - narrow[0])
