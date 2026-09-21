"""Paired significance tests between selectors on the same questions.

Every arm sees identical inputs, so paired tests are the right tool: a paired
bootstrap on mean support recall, and McNemar's exact test on the binary
full-support outcome.
"""

from __future__ import annotations

import argparse

import numpy as np
from eval_hotpot import embed_all, load_questions  # noqa: E402
from scipy import stats

from entropy_prune import EmbeddingEngine
from entropy_prune.evaluation import score_selection
from entropy_prune.selection import select_mmr, select_random, select_top_relevance


def paired_bootstrap(
    a: np.ndarray, b: np.ndarray, iters: int = 20000
) -> tuple[float, float]:
    """Bootstrap the paired mean difference ``a - b``; return mean and p-value."""
    diff = a - b
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(diff), size=(iters, len(diff)))
    means = diff[idx].mean(axis=1)
    p = 2 * min((means <= 0).mean(), (means >= 0).mean())
    return float(diff.mean()), float(min(1.0, p))


def main() -> None:
    """Compare MMR against top-k relevance and random at each compression level."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--questions", type=int, default=3000)
    args = ap.parse_args()

    qs = load_questions(args.parquet, args.questions)
    emb = embed_all(qs, EmbeddingEngine(), 256)
    split = max(1, int(0.3 * len(qs)))
    qs, emb = qs[split:], emb[split:]
    lam = 0.8  # tuned on the dev split by eval_hotpot.py

    print(f"paired tests on {len(qs)} held-out questions (lambda={lam})\n")
    print(
        f"{'target':>7} {'comparison':<26} {'mean diff':>10} {'p (boot)':>9} "
        f"{'McNemar b/c':>13} {'p (exact)':>10}"
    )
    for target in (0.3, 0.5, 0.7, 0.8, 0.9):
        rec = {k: [] for k in ("mmr", "top", "rand")}
        full = {k: [] for k in ("mmr", "top", "rand")}
        for seed, (q, (sim, rel)) in enumerate(zip(qs, emb, strict=True)):
            budget = max(1, int(round((1.0 - target) * sum(q.costs))))
            sels = {
                "mmr": select_mmr(sim, q.costs, budget, rel, lambda_=lam),
                "top": select_top_relevance(sim, q.costs, budget, rel),
                "rand": select_random(sim, q.costs, budget, seed=seed),
            }
            for k, kept in sels.items():
                r = score_selection(kept, q.gold, q.costs)
                rec[k].append(r.support_recall)
                full[k].append(r.fully_supported)
        arr = {k: np.array(v, float) for k, v in rec.items()}
        fl = {k: np.array(v, bool) for k, v in full.items()}

        for label, x, y in (
            ("mmr vs top_relevance", "mmr", "top"),
            ("mmr vs random", "mmr", "rand"),
        ):
            d, p = paired_bootstrap(arr[x], arr[y])
            b = int((fl[x] & ~fl[y]).sum())  # mmr wins, other loses
            c = int((~fl[x] & fl[y]).sum())  # other wins, mmr loses
            pm = stats.binomtest(b, b + c, 0.5).pvalue if (b + c) else 1.0
            print(
                f"{target:>7.0%} {label:<26} {d:>+10.4f} {p:>9.4f} "
                f"{f'{b}/{c}':>13} {pm:>10.2e}"
            )
        print()


if __name__ == "__main__":
    main()
