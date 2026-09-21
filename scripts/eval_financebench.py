"""Pruning on real SEC 10-K text with labelled ground truth (FinanceBench).

FinanceBench pairs questions about real 10-K filings with a gold answer and the
exact page of the filing that supports it. Its evidence pages are short, so a
realistic retrieval haystack is built the way HotpotQA's distractor setting is:
the gold page plus distractor pages drawn from *other* filings. The distractors
are real SEC text, the gold labels are human-written, and nothing is invented.

Metric is support recall against the labelled evidence snippet -- external
ground truth, not the coverage objective the selector optimises.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass

import numpy as np
import tiktoken

from entropy_prune import EmbeddingEngine, cosine_similarity_matrix
from entropy_prune.evaluation import aggregate, score_selection
from entropy_prune.selection import (
    select_greedy_coverage,
    select_mmr,
    select_random,
    select_threshold,
    select_top_relevance,
)

TARGETS = (0.5, 0.7, 0.8, 0.9)
_SENT = re.compile(r"(?<=[.!?])\s+")


def norm(text: str) -> str:
    """Collapse whitespace so page text and snippets compare reliably."""
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True, slots=True)
class FinQuestion:
    """One FinanceBench item with a distractor-padded context."""

    question: str
    answer: str
    company: str
    sentences: tuple[str, ...]
    gold: tuple[int, ...]
    costs: tuple[int, ...]


def build(path: str, distractors: int, seed: int = 0) -> list[FinQuestion]:
    """Load 10-K rows and pad each with distractor pages from other filings."""
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    rows = [r for r in rows if r.get("doc_type") == "10k"]

    pages: list[tuple[str, str]] = []  # (doc_name, page text)
    for r in rows:
        for e in r.get("evidence") or []:
            page = norm(e.get("evidence_text_full_page") or "")
            if len(page.split()) > 40:
                pages.append((r["doc_name"], page))

    encoder = tiktoken.get_encoding("cl100k_base")
    rng = np.random.default_rng(seed)
    out: list[FinQuestion] = []

    for r in rows:
        ev = [e for e in (r.get("evidence") or []) if e.get("evidence_text_full_page")]
        if not ev:
            continue
        gold_pages = [norm(e["evidence_text_full_page"]) for e in ev]
        snippets = [norm(e.get("evidence_text") or "") for e in ev]

        pool = [p for d, p in pages if d != r["doc_name"] and p not in gold_pages]
        if len(pool) < distractors:
            continue
        picks = rng.choice(len(pool), distractors, replace=False)
        blocks = gold_pages + [pool[i] for i in picks]
        order = rng.permutation(len(blocks))

        sentences: list[str] = []
        gold: list[int] = []
        for bi in order:
            block = blocks[bi]
            is_gold_block = bi < len(gold_pages)
            for s in _SENT.split(block):
                s = s.strip()
                if len(s.split()) < 4:
                    continue
                idx = len(sentences)
                sentences.append(s)
                if is_gold_block and any(s and s in snip for snip in snippets):
                    gold.append(idx)
        if not gold or len(sentences) < 25:
            continue
        costs = tuple(max(1, len(encoder.encode(s))) for s in sentences)
        out.append(
            FinQuestion(
                r["question"],
                str(r["answer"]),
                r.get("company", "?"),
                tuple(sentences),
                tuple(gold),
                costs,
            )
        )
    return out


def main() -> None:
    """Sweep compression over every selector on the SEC corpus."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--distractors", type=int, default=18)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    qs = build(args.jsonl, args.distractors)
    sizes = [len(q.sentences) for q in qs]
    toks = [sum(q.costs) for q in qs]
    print(f"{len(qs)} questions over {len({q.company for q in qs})} companies")
    print(f"  sentences/question: mean {np.mean(sizes):.0f} max {max(sizes)}")
    print(f"  tokens/question:    mean {np.mean(toks):.0f} max {max(toks)}")
    print(f"  gold sentences:     mean {np.mean([len(q.gold) for q in qs]):.1f}\n")

    engine = EmbeddingEngine()
    flat: list[str] = []
    spans: list[tuple[int, int]] = []
    for q in qs:
        start = len(flat)
        flat.append(q.question)
        flat.extend(q.sentences)
        spans.append((start, len(flat)))
    vectors = engine.encode(flat, batch_size=256, show_progress=True).vectors

    rows: dict[float, dict[str, dict[str, float]]] = {}
    for target in TARGETS:
        acc: dict[str, list] = {}
        for seed, (q, (s0, s1)) in enumerate(zip(qs, spans, strict=True)):
            chunks = vectors[s0 + 1 : s1]
            rel = (chunks @ vectors[s0]).astype(np.float64)
            sim = cosine_similarity_matrix(chunks)
            budget = max(1, int(round((1.0 - target) * sum(q.costs))))
            sels = {
                "random": select_random(sim, q.costs, budget, seed=seed),
                "top_relevance": select_top_relevance(sim, q.costs, budget, rel),
                "threshold": select_threshold(
                    sim, q.costs, budget, 0.85, relevance=rel
                ),
                "greedy_coverage": select_greedy_coverage(sim, q.costs, budget),
                "mmr": select_mmr(sim, q.costs, budget, rel, lambda_=0.8),
            }
            for name, kept in sels.items():
                acc.setdefault(name, []).append(score_selection(kept, q.gold, q.costs))
        rows[target] = {k: aggregate(v) for k, v in acc.items()}

    order = ["random", "threshold", "top_relevance", "greedy_coverage", "mmr"]
    print(
        f"\n{'target':>7} {'method':<18} {'compress':>9} {'supp.recall':>12} "
        f"{'full-support':>13}"
    )
    for target in TARGETS:
        best = max(rows[target], key=lambda k: rows[target][k]["support_recall"])
        for name in order:
            a = rows[target][name]
            mark = "  <-- best" if name == best else ""
            print(
                f"{target:>7.0%} {name:<18} {a['compression']:>9.1%} "
                f"{a['support_recall']:>12.4f} {a['full_support']:>13.4f}{mark}"
            )
        print()

    if args.out:
        with open(args.out, "w") as f:
            json.dump({str(k): v for k, v in rows.items()}, f, indent=2)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
