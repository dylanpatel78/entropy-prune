"""Paired significance for the end-to-end result.

The headline claim -- that pruning to 20% of tokens beats the full context --
rests on a few questions flipping. Same questions across arms, so paired tests
apply: bootstrap on mean F1 and McNemar's exact test on exact-match.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import torch
from eval_endtoend import MODEL, build_prompt, exact_match, generate, token_f1
from eval_hotpot import embed_all, load_questions
from scipy import stats
from transformers import AutoModelForCausalLM, AutoTokenizer

from entropy_prune import EmbeddingEngine
from entropy_prune.selection import select_random, select_top_relevance


def main() -> None:
    """Score three arms per question and run paired tests between them."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--questions", type=int, default=150)
    ap.add_argument("--target", type=float, default=0.8)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    qs = load_questions(args.parquet, args.questions * 2)[: args.questions]
    import pyarrow.parquet as pq

    lookup = {
        r["question"]: r["answer"]
        for r in pq.read_table(args.parquet, columns=["question", "answer"]).to_pylist()
    }
    gold = [lookup[q.question] for q in qs]
    emb = embed_all(qs, EmbeddingEngine(), 256)

    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    # fp16 on MPS: the full-context arm is ~5x longer prompts and dominates runtime
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16)
    model = model.to(device).eval()

    arms: dict[str, list[str]] = {"full": [], "pruned": [], "random": []}
    for seed, (q, (sim, rel)) in enumerate(zip(qs, emb, strict=True)):
        budget = max(1, int(round((1.0 - args.target) * sum(q.costs))))
        keep = select_top_relevance(sim, q.costs, budget, rel)
        rnd = select_random(sim, q.costs, budget, seed=seed)
        arms["full"].append(build_prompt(" ".join(q.sentences), q.question))
        arms["pruned"].append(
            build_prompt(" ".join(q.sentences[i] for i in keep), q.question)
        )
        arms["random"].append(
            build_prompt(" ".join(q.sentences[i] for i in rnd), q.question)
        )

    scores: dict[str, dict[str, np.ndarray]] = {}
    for name, prompts in arms.items():
        preds = generate(model, tok, prompts, device, args.batch)
        pairs = list(zip(preds, gold, strict=True))
        scores[name] = {
            "em": np.array([exact_match(p, a) for p, a in pairs]),
            "f1": np.array([token_f1(p, a) for p, a in pairs]),
        }
        print(
            f"  {name:<8} EM {scores[name]['em'].mean():.4f}  "
            f"F1 {scores[name]['f1'].mean():.4f}"
        )

    rng = np.random.default_rng(0)

    def boot(a: np.ndarray, b: np.ndarray, iters: int = 20000) -> tuple[float, float]:
        d = a - b
        idx = rng.integers(0, len(d), size=(iters, len(d)))
        m = d[idx].mean(axis=1)
        return float(d.mean()), float(
            min(1.0, 2 * min((m <= 0).mean(), (m >= 0).mean()))
        )

    print(f"\npaired tests, n={len(qs)}, target compression {args.target:.0%}")
    print(f"{'comparison':<24} {'dF1':>8} {'p(boot)':>9} {'McNemar b/c':>13} {'p':>8}")
    out = {}
    for label, x, y in (
        ("pruned vs full", "pruned", "full"),
        ("pruned vs random", "pruned", "random"),
        ("random vs full", "random", "full"),
    ):
        d, p = boot(scores[x]["f1"], scores[y]["f1"])
        b = int(((scores[x]["em"] == 1) & (scores[y]["em"] == 0)).sum())
        c = int(((scores[x]["em"] == 0) & (scores[y]["em"] == 1)).sum())
        pm = stats.binomtest(b, b + c, 0.5).pvalue if (b + c) else 1.0
        print(f"{label:<24} {d:>+8.4f} {p:>9.4f} {f'{b}/{c}':>13} {pm:>8.4f}")
        out[label] = {
            "delta_f1": d,
            "p_bootstrap": p,
            "mcnemar_b": b,
            "mcnemar_c": c,
            "p_mcnemar": float(pm),
        }

    if args.out:
        with open(args.out, "w") as f:
            json.dump(
                {
                    "n": len(qs),
                    "target": args.target,
                    "means": {
                        k: {m: float(v.mean()) for m, v in s.items()}
                        for k, s in scores.items()
                    },
                    "tests": out,
                },
                f,
                indent=2,
            )
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
