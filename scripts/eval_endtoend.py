"""End-to-end: does a model actually answer correctly on pruned context?

Support recall tells you the evidence survived. It does not tell you the model
then used it. This runs a small local LLM over pruned and full context and
measures answer accuracy against tokens spent -- the cost-versus-quality curve.

Uses Qwen2.5-0.5B-Instruct locally, so no API key and no per-run cost.
"""

from __future__ import annotations

import argparse
import json
import re
import string
import time
from collections import Counter
from collections.abc import Sequence

import numpy as np
import torch
from eval_hotpot import embed_all, load_questions  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer

from entropy_prune import EmbeddingEngine
from entropy_prune.selection import select_mmr, select_random, select_top_relevance

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
TARGETS = (0.5, 0.7, 0.8, 0.9)
METHODS = ("random", "top_relevance", "mmr")


def normalize(text: str) -> str:
    """SQuAD-style normalisation: lowercase, strip articles, punctuation, spaces."""
    text = text.lower()
    text = "".join(ch for ch in text if ch not in set(string.punctuation))
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def exact_match(pred: str, gold: str) -> float:
    """1.0 when the normalised strings match exactly."""
    return float(normalize(pred) == normalize(gold))


def token_f1(pred: str, gold: str) -> float:
    """Token-overlap F1 between prediction and gold answer."""
    p, g = normalize(pred).split(), normalize(gold).split()
    if not p or not g:
        return float(p == g)
    common = Counter(p) & Counter(g)
    same = sum(common.values())
    if same == 0:
        return 0.0
    precision, recall = same / len(p), same / len(g)
    return 2 * precision * recall / (precision + recall)


def build_prompt(context: str, question: str) -> str:
    """One QA prompt over the supplied context."""
    return (
        f"Context:\n{context}\n\nQuestion: {question}\n\n"
        "Answer using only the context. Reply with a short phrase, nothing else."
    )


def generate(
    model: AutoModelForCausalLM,
    tok: AutoTokenizer,
    prompts: Sequence[str],
    device: str,
    batch_size: int,
    max_new: int = 24,
) -> list[str]:
    """Greedy-decode answers for a list of prompts, batched."""
    outs: list[str] = []
    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        texts = [
            tok.apply_chat_template(
                [{"role": "user", "content": p}],
                tokenize=False,
                add_generation_prompt=True,
            )
            for p in chunk
        ]
        enc = tok(
            texts, return_tensors="pt", padding=True, truncation=True, max_length=3072
        ).to(device)
        with torch.no_grad():
            gen = model.generate(
                **enc,
                max_new_tokens=max_new,
                do_sample=False,
                pad_token_id=tok.pad_token_id,
            )
        for i in range(len(chunk)):
            outs.append(
                tok.decode(
                    gen[i][enc["input_ids"].shape[1] :], skip_special_tokens=True
                ).strip()
            )
    return outs


def main() -> None:
    """Run every condition and print accuracy against tokens spent."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--questions", type=int, default=150)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    qs = load_questions(args.parquet, args.questions * 2)[: args.questions]
    answers = _load_answers(args.parquet, qs)
    emb = embed_all(qs, EmbeddingEngine(), 256)

    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)
    model = model.to(device).eval()
    print(f"{MODEL} on {device} | {len(qs)} questions\n")

    conditions: dict[str, list[str]] = {}
    tokens_used: dict[str, list[int]] = {}

    conditions["full"] = [build_prompt(" ".join(q.sentences), q.question) for q in qs]
    tokens_used["full"] = [sum(q.costs) for q in qs]

    for target in TARGETS:
        for method in METHODS:
            prompts, toks = [], []
            for seed, (q, (sim, rel)) in enumerate(zip(qs, emb, strict=True)):
                budget = max(1, int(round((1.0 - target) * sum(q.costs))))
                if method == "random":
                    kept = select_random(sim, q.costs, budget, seed=seed)
                elif method == "top_relevance":
                    kept = select_top_relevance(sim, q.costs, budget, rel)
                else:
                    kept = select_mmr(sim, q.costs, budget, rel, lambda_=0.8)
                prompts.append(
                    build_prompt(" ".join(q.sentences[i] for i in kept), q.question)
                )
                toks.append(sum(q.costs[i] for i in kept))
            conditions[f"{target:.0%}|{method}"] = prompts
            tokens_used[f"{target:.0%}|{method}"] = toks

    results: dict[str, dict[str, float]] = {}
    for name, prompts in conditions.items():
        t0 = time.perf_counter()
        preds = generate(model, tok, prompts, device, args.batch)
        em = float(
            np.mean([exact_match(p, a) for p, a in zip(preds, answers, strict=True)])
        )
        f1 = float(
            np.mean([token_f1(p, a) for p, a in zip(preds, answers, strict=True)])
        )
        mean_tok = float(np.mean(tokens_used[name]))
        results[name] = {"em": em, "f1": f1, "tokens": mean_tok}
        print(
            f"  {name:<20} EM {em:.4f}  F1 {f1:.4f}  tokens {mean_tok:>7.0f}  "
            f"({time.perf_counter() - t0:.0f}s)"
        )

    base_tok = results["full"]["tokens"]
    base_f1 = results["full"]["f1"]
    header = (
        f"\n{'condition':<20} {'tokens':>8} {'saved':>7} "
        f"{'EM':>7} {'F1':>7} {'F1 kept':>8}"
    )
    print(header)
    print(
        f"{'full context':<20} {base_tok:>8.0f} {'0%':>7} "
        f"{results['full']['em']:>7.4f} {base_f1:>7.4f} {'100.0%':>8}"
    )
    for target in TARGETS:
        for method in METHODS:
            r = results[f"{target:.0%}|{method}"]
            print(
                f"{f'{target:.0%} {method}':<20} {r['tokens']:>8.0f} "
                f"{1 - r['tokens'] / base_tok:>6.0%} {r['em']:>7.4f} {r['f1']:>7.4f} "
                f"{r['f1'] / base_f1:>7.1%}"
            )
        print()

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"wrote {args.out}")


def _load_answers(path: str, questions: Sequence) -> list[str]:
    """Recover the gold answer string for each sampled question."""
    import pyarrow.parquet as pq

    table = pq.read_table(path, columns=["question", "answer"]).to_pylist()
    lookup = {r["question"]: r["answer"] for r in table}
    return [lookup[q.question] for q in questions]


if __name__ == "__main__":
    main()
