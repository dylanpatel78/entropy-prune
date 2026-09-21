"""Does diversity-based pruning win when the task is coverage, not lookup?

HotpotQA showed diversity losing badly: there is a query, and the most
*distinct* chunk is usually the most *irrelevant*. Multi-News is the opposite
condition -- several source articles about one event, no query, and the goal is
to cover everything the reference summary mentions.

If greedy facility location wins here and loses on QA, the finding stops being
"diversity does not work" and becomes "diversity helps coverage tasks,
relevance helps lookup tasks", which is a claim about *when* to use each.

Ground truth is the human reference summary, which the selector never sees --
so this is not the circular self-scoring the pruner's own objective would give.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import tiktoken

from entropy_prune import EmbeddingEngine, cosine_similarity_matrix
from entropy_prune.selection import (
    select_greedy_coverage,
    select_mmr,
    select_random,
    select_threshold,
    select_top_relevance,
)

TARGETS = (0.5, 0.7, 0.8, 0.9)
_SENT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True, slots=True)
class Article:
    """One Multi-News item: source sentences plus its reference summary."""

    sentences: tuple[str, ...]
    costs: tuple[int, ...]
    summary: str


def clean(text: str) -> str:
    """Strip the dataset's placeholder tokens and collapse whitespace."""
    text = text.replace("NEWLINE_CHAR", " ").replace("|||||", " ")
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str, min_words: int = 4) -> list[str]:
    """Split into sentences, dropping fragments too short to carry content."""
    return [s.strip() for s in _SENT.split(text) if len(s.split()) >= min_words]


def load_articles(
    src_path: str, tgt_path: str, limit: int, max_sents: int, seed: int = 0
) -> list[Article]:
    """Read a random sample of Multi-News items into chunk form."""
    with open(src_path, encoding="utf-8") as f:
        srcs = f.read().splitlines()
    with open(tgt_path, encoding="utf-8") as f:
        tgts = f.read().splitlines()

    picks = np.random.default_rng(seed).choice(
        len(srcs), min(limit * 3, len(srcs)), replace=False
    )
    encoder = tiktoken.get_encoding("cl100k_base")
    out: list[Article] = []
    for i in picks:
        sents = split_sentences(clean(srcs[i]))[:max_sents]
        summary = clean(tgts[i]).lstrip("– ").strip()
        if len(sents) < 20 or len(summary.split()) < 30:
            continue  # too short to be a meaningful pruning problem
        costs = tuple(max(1, len(encoder.encode(s))) for s in sents)
        out.append(Article(tuple(sents), costs, summary))
        if len(out) >= limit:
            break
    return out


def ngrams(text: str, n: int) -> set[tuple[str, ...]]:
    """Lowercased word n-grams of ``text``."""
    words = _WORD.findall(text.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def rouge_recall(reference: str, candidate: str, n: int) -> float:
    """Fraction of the reference's n-grams that appear in the candidate."""
    ref = ngrams(reference, n)
    if not ref:
        return 0.0
    return len(ref & ngrams(candidate, n)) / len(ref)


def semantic_coverage(
    summary_vectors: np.ndarray, chunk_vectors: np.ndarray, kept: Sequence[int]
) -> float:
    """Mean best-match of each reference summary sentence to a surviving chunk.

    The facility-location objective measured against *external* ground truth
    instead of against the source itself.
    """
    if len(kept) == 0:
        return 0.0
    sims = summary_vectors @ chunk_vectors[np.asarray(kept, dtype=np.intp)].T
    return float(sims.max(axis=1).mean())


def main() -> None:
    """Sweep compression targets over every selector and report."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--tgt", required=True)
    ap.add_argument("--articles", type=int, default=400)
    ap.add_argument("--max-sents", type=int, default=120)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    arts = load_articles(args.src, args.tgt, args.articles, args.max_sents)
    sizes = [len(a.sentences) for a in arts]
    print(
        f"loaded {len(arts)} articles | sentences: mean {np.mean(sizes):.1f} "
        f"max {max(sizes)} | tokens: mean {np.mean([sum(a.costs) for a in arts]):.0f}"
    )

    engine = EmbeddingEngine()
    flat: list[str] = []
    spans: list[tuple[int, int, int]] = []
    for a in arts:
        start = len(flat)
        flat.extend(a.sentences)
        mid = len(flat)
        flat.extend(split_sentences(a.summary, min_words=3) or [a.summary])
        spans.append((start, mid, len(flat)))

    t0 = time.perf_counter()
    vectors = engine.encode(flat, batch_size=256, show_progress=True).vectors
    print(
        f"embedded {len(flat)} sentences on {engine.device} "
        f"in {time.perf_counter() - t0:.1f}s\n"
    )

    rows: dict[float, dict[str, dict[str, float]]] = {}
    for target in TARGETS:
        acc: dict[str, list[tuple[float, float, float]]] = {}
        for seed, (a, (s0, s1, s2)) in enumerate(zip(arts, spans, strict=True)):
            chunks = vectors[s0:s1]
            summary_vecs = vectors[s1:s2]
            sim = cosine_similarity_matrix(chunks)
            centroid = chunks.mean(axis=0)
            centroid = centroid / max(float(np.linalg.norm(centroid)), 1e-12)
            rel = (chunks @ centroid).astype(np.float64)
            budget = max(1, int(round((1.0 - target) * sum(a.costs))))

            lead: list[int] = []
            spent = 0
            for i in range(len(a.sentences)):
                if spent + a.costs[i] <= budget:
                    lead.append(i)
                    spent += a.costs[i]

            sels = {
                "random": select_random(sim, a.costs, budget, seed=seed),
                "lead_k": lead,
                "centroid_relevance": select_top_relevance(sim, a.costs, budget, rel),
                "threshold": select_threshold(
                    sim, a.costs, budget, 0.75, relevance=rel
                ),
                "greedy_coverage": select_greedy_coverage(sim, a.costs, budget),
                "mmr": select_mmr(sim, a.costs, budget, rel, lambda_=0.5),
            }
            for name, kept in sels.items():
                text = " ".join(a.sentences[i] for i in kept)
                acc.setdefault(name, []).append(
                    (
                        rouge_recall(a.summary, text, 1),
                        rouge_recall(a.summary, text, 2),
                        semantic_coverage(summary_vecs, chunks, kept),
                    )
                )
        rows[target] = {
            k: {
                "rouge1_recall": float(np.mean([x[0] for x in v])),
                "rouge2_recall": float(np.mean([x[1] for x in v])),
                "semantic_coverage": float(np.mean([x[2] for x in v])),
            }
            for k, v in acc.items()
        }

    order = [
        "random",
        "lead_k",
        "centroid_relevance",
        "threshold",
        "greedy_coverage",
        "mmr",
    ]
    print(
        f"{'target':>7} {'method':<20} {'ROUGE-1 rec':>12} {'ROUGE-2 rec':>12} "
        f"{'sem.coverage':>13}"
    )
    for target in TARGETS:
        best = max(rows[target], key=lambda k: rows[target][k]["rouge1_recall"])
        for name in order:
            r = rows[target][name]
            mark = "  <-- best" if name == best else ""
            print(
                f"{target:>7.0%} {name:<20} {r['rouge1_recall']:>12.4f} "
                f"{r['rouge2_recall']:>12.4f} {r['semantic_coverage']:>13.4f}{mark}"
            )
        print()

    if args.out:
        with open(args.out, "w") as f:
            json.dump({str(k): v for k, v in rows.items()}, f, indent=2)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
