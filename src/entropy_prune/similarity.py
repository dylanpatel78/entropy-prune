"""Cosine similarity matrix computation.

For an embedding matrix ``E`` with unit-norm rows, the pairwise cosine
similarity matrix is exactly the Gram matrix ``S = E @ E.T``. That
identity is the load-bearing fact of this module: it means the same
object serves as (a) a redundancy map for greedy pruning and (b) the
matrix whose eigendecomposition equals the squared singular spectrum of
``E``, which Module 2 consumes for subspace pruning.
"""

from __future__ import annotations

import numpy as np
import torch

from entropy_prune.embeddings import l2_normalize


def cosine_similarity_matrix(
    vectors: np.ndarray,
    assume_normalized: bool = True,
    device: str | None = None,
) -> np.ndarray:
    """Compute the dense ``(n, n)`` pairwise cosine similarity matrix.

    Args:
        vectors: Embedding matrix of shape ``(n, d)``.
        assume_normalized: Skip re-normalization when rows are already
            unit-norm. Set ``False`` for raw encoder output.
        device: When given, run the matmul on this torch device.
            ``None`` keeps the computation in NumPy/BLAS on the CPU.

    Returns:
        Symmetric array of shape ``(n, n)``, dtype ``float32``, with
        entries in ``[-1, 1]`` and an exact unit diagonal.
    """
    unit = vectors if assume_normalized else l2_normalize(vectors)

    if device is None:
        gram = unit @ unit.T
    else:
        tensor = torch.from_numpy(np.ascontiguousarray(unit)).to(device)
        gram = (tensor @ tensor.T).cpu().numpy()

    gram = np.clip(gram, -1.0, 1.0)
    gram = 0.5 * (gram + gram.T)
    np.fill_diagonal(gram, 1.0)
    return gram.astype(np.float32, copy=False)


def off_diagonal_mask(n: int) -> np.ndarray:
    """Boolean ``(n, n)`` mask that is ``True`` everywhere off the diagonal.

    Args:
        n: Matrix order.

    Returns:
        Array of shape ``(n, n)`` and dtype ``bool``.
    """
    return ~np.eye(n, dtype=bool)


def redundancy_scores(similarity: np.ndarray) -> np.ndarray:
    """Mean off-diagonal similarity of each chunk to all others.

    High values flag chunks whose semantic content is already covered
    elsewhere in the context window.

    Args:
        similarity: Symmetric cosine matrix of shape ``(n, n)``.

    Returns:
        Array of shape ``(n,)``, dtype ``float32``.
    """
    n = _validate_square(similarity)
    if n == 1:
        return np.zeros(1, dtype=np.float32)
    row_sums = similarity.sum(axis=1) - np.diagonal(similarity)
    return (row_sums / (n - 1)).astype(np.float32, copy=False)


def max_similarity_scores(similarity: np.ndarray) -> np.ndarray:
    """Largest off-diagonal similarity for each chunk (nearest neighbour).

    Args:
        similarity: Symmetric cosine matrix of shape ``(n, n)``.

    Returns:
        Array of shape ``(n,)``, dtype ``float32``.
    """
    n = _validate_square(similarity)
    if n == 1:
        return np.full(1, -1.0, dtype=np.float32)
    masked = np.where(off_diagonal_mask(n), similarity, -np.inf)
    return masked.max(axis=1).astype(np.float32, copy=False)


def duplicate_pairs(
    similarity: np.ndarray,
    threshold: float = 0.95,
) -> list[tuple[int, int, float]]:
    """List upper-triangle pairs whose similarity exceeds ``threshold``.

    Args:
        similarity: Symmetric cosine matrix of shape ``(n, n)``.
        threshold: Inclusive lower bound on cosine similarity.

    Returns:
        Tuples ``(i, j, score)`` with ``i < j``, sorted by descending score.
    """
    n = _validate_square(similarity)
    rows, cols = np.triu_indices(n, k=1)
    scores = similarity[rows, cols]
    hits = scores >= threshold
    pairs = [
        (int(i), int(j), float(s))
        for i, j, s in zip(rows[hits], cols[hits], scores[hits], strict=True)
    ]
    return sorted(pairs, key=lambda pair: pair[2], reverse=True)


def _validate_square(similarity: np.ndarray) -> int:
    """Assert ``similarity`` is square and 2-D, returning its order ``n``.

    Args:
        similarity: Candidate matrix.

    Returns:
        The matrix order ``n``.
    """
    if similarity.ndim != 2 or similarity.shape[0] != similarity.shape[1]:
        raise ValueError(f"expected a square matrix, got shape {similarity.shape}")
    return similarity.shape[0]
