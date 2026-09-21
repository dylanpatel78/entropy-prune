"""Context pruning via entropy, SVD subspaces, and cosine similarity.

The similarity, selection and evaluation layers are pure NumPy. The encoder
pulls in torch and sentence-transformers, so it is imported lazily -- you can
``pip install entropy-prune`` and bring your own vectors without a 2 GB
dependency, or ``pip install entropy-prune[embeddings]`` to get the encoder.
"""

from typing import TYPE_CHECKING, Any

from entropy_prune.evaluation import (
    PruneResult,
    aggregate,
    score_selection,
    wilson_interval,
)
from entropy_prune.selection import (
    coverage_score,
    select_greedy_coverage,
    select_mmr,
    select_random,
    select_threshold,
    select_top_relevance,
)
from entropy_prune.similarity import (
    cosine_similarity_matrix,
    duplicate_pairs,
    l2_normalize,
    max_similarity_scores,
    redundancy_scores,
)

if TYPE_CHECKING:  # pragma: no cover
    from entropy_prune.embeddings import (
        DEFAULT_MODEL_NAME,
        EmbeddingEngine,
        EmbeddingMatrix,
        resolve_device,
    )

_LAZY = {
    "DEFAULT_MODEL_NAME",
    "EmbeddingEngine",
    "EmbeddingMatrix",
    "resolve_device",
}


def __getattr__(name: str) -> Any:
    """Import the encoder layer on first use, with a clear error if absent."""
    if name in _LAZY:
        try:
            from entropy_prune import embeddings
        except ImportError as exc:  # pragma: no cover - depends on install extras
            raise ImportError(
                f"{name} needs the encoder extra: pip install entropy-prune[embeddings]"
            ) from exc
        return getattr(embeddings, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DEFAULT_MODEL_NAME",
    "EmbeddingEngine",
    "EmbeddingMatrix",
    "PruneResult",
    "aggregate",
    "cosine_similarity_matrix",
    "coverage_score",
    "duplicate_pairs",
    "l2_normalize",
    "max_similarity_scores",
    "redundancy_scores",
    "resolve_device",
    "score_selection",
    "select_greedy_coverage",
    "select_mmr",
    "select_random",
    "select_threshold",
    "select_top_relevance",
    "wilson_interval",
]
__version__ = "0.2.0"
