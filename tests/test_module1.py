"""Tests for Module 1: embedding matrix and cosine similarity."""

from __future__ import annotations

import numpy as np
import pytest

from entropy_prune.embeddings import EmbeddingMatrix, l2_normalize
from entropy_prune.similarity import (
    cosine_similarity_matrix,
    duplicate_pairs,
    max_similarity_scores,
    redundancy_scores,
)


def test_l2_normalize_gives_unit_rows() -> None:
    raw = np.array([[3.0, 4.0], [0.0, 0.0], [-1.0, 0.0]], dtype=np.float32)
    unit = l2_normalize(raw)
    assert unit.dtype == np.float32
    np.testing.assert_allclose(unit[0], [0.6, 0.8], atol=1e-6)
    np.testing.assert_allclose(unit[1], [0.0, 0.0], atol=1e-6)
    np.testing.assert_allclose(np.linalg.norm(unit[[0, 2]], axis=1), 1.0, atol=1e-6)


def test_similarity_matrix_properties() -> None:
    rng = np.random.default_rng(7)
    unit = l2_normalize(rng.normal(size=(12, 32)).astype(np.float32))
    sim = cosine_similarity_matrix(unit)
    assert sim.shape == (12, 12)
    np.testing.assert_allclose(np.diagonal(sim), 1.0, atol=1e-6)
    np.testing.assert_allclose(sim, sim.T, atol=1e-7)
    assert sim.min() >= -1.0 and sim.max() <= 1.0
    assert np.linalg.eigvalsh(sim.astype(np.float64)).min() > -1e-6


def test_orthogonal_rows_are_uncorrelated() -> None:
    unit = np.eye(4, dtype=np.float32)
    sim = cosine_similarity_matrix(unit)
    np.testing.assert_allclose(sim, np.eye(4), atol=1e-6)
    np.testing.assert_allclose(redundancy_scores(sim), 0.0, atol=1e-6)


def test_duplicate_detection_and_scores() -> None:
    base = l2_normalize(np.array([[1.0, 0.0], [1.0, 0.01], [0.0, 1.0]], np.float32))
    sim = cosine_similarity_matrix(base)
    pairs = duplicate_pairs(sim, threshold=0.95)
    assert pairs and pairs[0][:2] == (0, 1)
    assert max_similarity_scores(sim)[0] == pytest.approx(sim[0, 1], abs=1e-6)


def test_embedding_matrix_rejects_misaligned_texts() -> None:
    vectors = np.zeros((2, 4), dtype=np.float32)
    with pytest.raises(ValueError, match="does not match"):
        EmbeddingMatrix(vectors=vectors, texts=("only one",), model_name="stub")


def test_select_preserves_alignment() -> None:
    vectors = l2_normalize(np.arange(12, dtype=np.float32).reshape(3, 4) + 1.0)
    matrix = EmbeddingMatrix(vectors, ("a", "b", "c"), "stub")
    subset = matrix.select([2, 0])
    assert subset.texts == ("c", "a")
    np.testing.assert_allclose(subset.vectors[0], vectors[2])
