"""Evaluate context pruning on HotpotQA (distractor setting).

Each question ships 10 paragraphs, only 2 of which are relevant, and the
benchmark labels the exact sentences required to answer. So we can measure
whether pruning keeps the information the task needs -- without an LLM, and
without scoring against the objective the pruner itself optimises.

Baseline hyperparameters (threshold tau, MMR lambda) are tuned on a dev split
and applied unchanged to a held-out test split. Tuning our method while leaving
a baseline at its default is the standard way to manufacture a win.

Usage:
    python scripts/eval_hotpot.py --parquet <path> --questions 500
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
import pyarrow.parquet as pq
import tiktoken

from entropy_prune import EmbeddingEngine, cosine_similarity_matrix
from entropy_prune.evaluation import aggregate, score_selection, wilson_interval
from entropy_prune.selection import (
    select_greedy_coverage,
    select_mmr,
    select_random,
    select_threshold,
    select_top_relevance,
)

TARGETS = (0.3, 0.5, 0.7, 0.8, 0.9)


@dataclass(frozen=True, slots=True)
class Question:
    """One HotpotQA item flattened into sentence-level chunks."""

    question: str
    sentences: tuple[str, ...]
    gold: tuple[int, ...]
    costs: tuple[int, ...]


def load_questions(path: str, limit: int, seed: int = 0) -> list[Question]:
    """Read the parquet file and flatten a random sample into chunk form."""
    table = pq.read_table(path, columns=["question", "supporting_facts", "context"])
    total = table.num_rows
    picks = np.random.default_rng(seed).choice(total, min(limit, total), replace=False)
    rows = table.take(np.sort(picks)).to_pylist()
    encoder = tiktoken.get_encoding("cl100k_base")

    out: list[Question] = []
    for row in rows:
        titles = row["context"]["title"]
        paragraphs = row["context"]["sentences"]
        sentences: list[str] = []
        index_of: dict[tuple[str, int], int] = {}
        for title, sents in zip(titles, paragraphs, strict=True):
            for sent_id, sent in enumerate(sents):
                index_of[(title, sent_id)] = len(sentences)
                sentences.append(sent)

        facts = row["supporting_facts"]
        gold = [
            index_of[(t, s)]
            for t, s in zip(facts["title"], facts["sent_id"], strict=True)
            if (t, s) in index_of
        ]
        if not gold or len(sentences) < 4:
            continue  # unusable item: no resolvable gold, or nothing to prune
        costs = [max(1, len(encoder.encode(s))) for s in sentences]
        out.append(
            Question(row["question"], tuple(sentences), tuple(gold), tuple(costs))
        )
    return out


def embed_all(
    questions: Sequence[Question], engine: EmbeddingEngine, batch: int
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Embed every question and its sentences in one pass.

    Returns:
        Per question, its ``(n, n)`` similarity matrix and ``(n,)`` relevance.
    """
    flat: list[str] = []
    spans: list[tuple[int, int]] = []
    for q in questions:
        start = len(flat)
        flat.append(q.question)
        flat.extend(q.sentences)
        spans.append((start, len(flat)))

    vectors = engine.encode(flat, batch_size=batch, show_progress=True).vectors
    out = []
    for start, end in spans:
        query = vectors[start]
        chunk_vectors = vectors[start + 1 : end]
        out.append(
            (
                cosine_similarity_matrix(chunk_vectors),
                (chunk_vectors @ query).astype(np.float64),
            )
        )
    return out


def run_selectors(
    q: Question,
    sim: np.ndarray,
    rel: np.ndarray,
    budget: int,
    tau: float,
    lam: float,
    seed: int,
) -> dict[str, list[int]]:
    """Run every selector at one budget and return their kept sets."""
    costs = q.costs
    return {
        "random": select_random(sim, costs, budget, seed=seed),
        "top_relevance": select_top_relevance(sim, costs, budget, rel),
        "threshold": select_threshold(sim, costs, budget, tau, relevance=rel),
        "greedy_coverage": select_greedy_coverage(sim, costs, budget),
        "mmr": select_mmr(sim, costs, budget, rel, lambda_=lam),
    }


def evaluate(
    questions: Sequence[Question],
    embedded: Sequence[tuple[np.ndarray, np.ndarray]],
    tau: float,
    lam: float,
) -> dict[float, dict[str, dict[str, float]]]:
    """Sweep compression targets, returning aggregates per target per method."""
    table: dict[float, dict[str, dict[str, float]]] = {}
    for target in TARGETS:
        buckets: dict[str, list] = {}
        for seed, (q, (sim, rel)) in enumerate(zip(questions, embedded, strict=True)):
            budget = max(1, int(round((1.0 - target) * sum(q.costs))))
            for name, kept in run_selectors(
                q, sim, rel, budget, tau, lam, seed
            ).items():
                buckets.setdefault(name, []).append(
                    score_selection(kept, q.gold, q.costs)
                )
        table[target] = {k: aggregate(v) for k, v in buckets.items()}
    return table


def tune_aggregate(
    questions: Sequence[Question],
    embedded: Sequence[tuple[np.ndarray, np.ndarray]],
) -> tuple[float, float]:
    """Pick tau and lambda maximising MEAN dev support recall, not per-item."""

    def mean_recall(fn: Callable[..., list[int]]) -> float:
        scores = []
        for target in (0.5, 0.8):
            for q, (sim, rel) in zip(questions, embedded, strict=True):
                budget = max(1, int(round((1.0 - target) * sum(q.costs))))
                kept = fn(sim, q.costs, budget, rel)
                scores.append(score_selection(kept, q.gold, q.costs).support_recall)
        return float(np.mean(scores))

    taus = np.arange(0.30, 1.01, 0.05)
    tau_scores = [
        mean_recall(
            lambda s, c, b, r, t=float(t): select_threshold(s, c, b, t, relevance=r)
        )
        for t in taus
    ]
    lams = np.arange(0.0, 1.01, 0.1)
    lam_scores = [
        mean_recall(lambda s, c, b, r, x=float(x): select_mmr(s, c, b, r, lambda_=x))
        for x in lams
    ]
    return float(taus[int(np.argmax(tau_scores))]), float(
        lams[int(np.argmax(lam_scores))]
    )


def main() -> None:
    """Run the sweep and print a report."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--questions", type=int, default=500)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    t0 = time.perf_counter()
    questions = load_questions(args.parquet, args.questions)
    print(f"loaded {len(questions)} questions in {time.perf_counter() - t0:.1f}s")
    sizes = [len(q.sentences) for q in questions]
    tokens = [sum(q.costs) for q in questions]
    print(
        f"  sentences/question: mean {np.mean(sizes):.1f} max {max(sizes)}\n"
        f"  tokens/question:    mean {np.mean(tokens):.0f}\n"
        f"  gold sentences:     mean {np.mean([len(q.gold) for q in questions]):.2f}"
    )

    engine = EmbeddingEngine()
    t1 = time.perf_counter()
    embedded = embed_all(questions, engine, args.batch)
    embed_s = time.perf_counter() - t1
    print(
        f"embedded on {engine.device} in {embed_s:.1f}s "
        f"({embed_s / len(questions) * 1000:.1f} ms/question)"
    )

    split = max(1, int(0.3 * len(questions)))
    dev_q, dev_e = questions[:split], embedded[:split]
    test_q, test_e = questions[split:], embedded[split:]
    tau, lam = tune_aggregate(dev_q, dev_e)
    print(f"tuned on {len(dev_q)} dev questions: tau={tau:.2f}  lambda={lam:.1f}")
    print(f"evaluating on {len(test_q)} held-out questions\n")

    t2 = time.perf_counter()
    table = evaluate(test_q, test_e, tau, lam)
    prune_s = time.perf_counter() - t2
    per_call = prune_s / (len(test_q) * len(TARGETS) * 5) * 1000

    order = ["random", "threshold", "top_relevance", "greedy_coverage", "mmr"]
    print(
        f"{'target':>7} {'method':<17} {'compress':>9} {'supp.recall':>12} "
        f"{'full-support':>13} {'95% CI':>16}"
    )
    for target in TARGETS:
        for name in order:
            a = table[target][name]
            lo, hi = wilson_interval(round(a["full_support"] * a["n"]), int(a["n"]))
            print(
                f"{target:>7.0%} {name:<17} {a['compression']:>9.1%} "
                f"{a['support_recall']:>12.4f} {a['full_support']:>13.4f} "
                f"{f'[{lo:.3f}, {hi:.3f}]':>16}"
            )
        print()

    print(f"pruning cost: {per_call:.2f} ms per document per method")
    print(f"embedding cost: {embed_s / len(questions) * 1000:.1f} ms per document")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(
                {
                    "tau": tau,
                    "lambda": lam,
                    "n_test": len(test_q),
                    "table": {str(k): v for k, v in table.items()},
                },
                f,
                indent=2,
            )
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
