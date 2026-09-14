"""Context pruning via entropy, SVD subspaces, and cosine similarity."""

from entropy_prune.embeddings import (
    DEFAULT_MODEL_NAME,
    EmbeddingEngine,
    EmbeddingMatrix,
    l2_normalize,
    resolve_device,
)
from entropy_prune.similarity import (
    cosine_similarity_matrix,
    duplicate_pairs,
    max_similarity_scores,
    redundancy_scores,
)

__all__ = [
    "DEFAULT_MODEL_NAME",
    "EmbeddingEngine",
    "EmbeddingMatrix",
    "cosine_similarity_matrix",
    "duplicate_pairs",
    "l2_normalize",
    "max_similarity_scores",
    "redundancy_scores",
    "resolve_device",
]
__version__ = "0.1.0"
