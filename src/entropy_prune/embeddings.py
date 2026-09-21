"""Sentence embedding matrix generation.

Turns an ordered collection of context chunks into a dense matrix
``E`` of shape ``(n_chunks, d_model)`` whose rows are unit-norm
semantic vectors. Every downstream stage of the pruner (cosine
similarity, SVD subspace decomposition, entropy scoring) consumes this
single object, so the invariants are enforced here and nowhere else.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from entropy_prune.similarity import l2_normalize

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def resolve_device(preferred: str | None = None) -> str:
    """Return the best available torch device string.

    Args:
        preferred: Explicit override, e.g. ``"cuda"``, ``"mps"``, ``"cpu"``.
            When ``None`` the fastest available backend is selected.

    Returns:
        A device string suitable for ``torch.device`` and
        ``SentenceTransformer(device=...)``.
    """
    if preferred is not None:
        return preferred
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@dataclass(frozen=True, slots=True)
class EmbeddingMatrix:
    """An embedding matrix bound to the texts that produced it.

    Attributes:
        vectors: Array of shape ``(n, d)``, dtype ``float32``, unit rows.
        texts: The ``n`` source chunks, index-aligned with ``vectors``.
        model_name: Identifier of the encoder, recorded for reproducibility.
    """

    vectors: np.ndarray
    texts: tuple[str, ...]
    model_name: str

    def __post_init__(self) -> None:
        if self.vectors.ndim != 2:
            raise ValueError(f"vectors must be 2-D, got shape {self.vectors.shape}")
        if self.vectors.shape[0] != len(self.texts):
            raise ValueError(
                f"row count {self.vectors.shape[0]} does not match "
                f"{len(self.texts)} texts"
            )
        if self.vectors.dtype != np.float32:
            raise ValueError(f"vectors must be float32, got {self.vectors.dtype}")

    @property
    def n_chunks(self) -> int:
        """Number of context chunks (rows)."""
        return self.vectors.shape[0]

    @property
    def d_model(self) -> int:
        """Embedding dimensionality (columns)."""
        return self.vectors.shape[1]

    def select(self, indices: Sequence[int]) -> EmbeddingMatrix:
        """Return a new matrix restricted to ``indices``, order preserved.

        Args:
            indices: Row positions to keep.

        Returns:
            A fresh :class:`EmbeddingMatrix` holding only those rows.
        """
        index_array = np.asarray(indices, dtype=np.intp)
        return EmbeddingMatrix(
            vectors=self.vectors[index_array],
            texts=tuple(self.texts[i] for i in index_array),
            model_name=self.model_name,
        )


class EmbeddingEngine:
    """Stateful wrapper that encodes text chunks into an embedding matrix.

    The transformer is loaded once and reused, because model
    instantiation dominates the cost of encoding small batches.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str | None = None,
    ) -> None:
        """Load the encoder onto the chosen device.

        Args:
            model_name: Any SentenceTransformers-compatible checkpoint.
            device: Torch device string; auto-detected when ``None``.
        """
        self.model_name = model_name
        self.device = resolve_device(device)
        self._model = SentenceTransformer(model_name, device=self.device)

    @property
    def d_model(self) -> int:
        """Output dimensionality of the loaded encoder."""
        return int(self._model.get_sentence_embedding_dimension())

    def encode(
        self,
        texts: Sequence[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> EmbeddingMatrix:
        """Embed ``texts`` into a unit-norm matrix of shape ``(n, d)``.

        Args:
            texts: Ordered context chunks. Must be non-empty.
            batch_size: Rows per forward pass; trades memory for speed.
            show_progress: Emit a tqdm bar during encoding.

        Returns:
            An :class:`EmbeddingMatrix` with L2-normalized rows.
        """
        if len(texts) == 0:
            raise ValueError("cannot embed an empty sequence of texts")

        raw: np.ndarray = self._model.encode(
            list(texts),
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=False,
            show_progress_bar=show_progress,
        )
        return EmbeddingMatrix(
            vectors=l2_normalize(raw),
            texts=tuple(texts),
            model_name=self.model_name,
        )
