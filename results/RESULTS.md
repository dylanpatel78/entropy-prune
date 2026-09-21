# Evaluation results

**Benchmark:** HotpotQA dev, distractor setting. Each question ships 10
paragraphs (2 gold, 8 distractors) and labels the exact sentences required to
answer. Chunks are sentences; token costs are `tiktoken` `cl100k_base`.

**Protocol:** 3,000 questions sampled with a fixed seed. The first 900 are a
dev split used only to tune baseline hyperparameters (`tau`, `lambda`); all
figures below are on the **2,100 held-out questions**. Every baseline is tuned
on the same dev split — tuning only your own method is how benchmark claims get
faked.

**Metric:** support recall — the fraction of the benchmark's required sentences
that survive pruning. This is external ground truth, deliberately *not* the
coverage or effective-rank objectives the selector optimises, which would be
circular.

**Corpus stats:** 41.0 sentences/question (max 147), 1,240 tokens/question,
2.41 required sentences/question.

## Support recall vs compression

| Compression | random | threshold | top-k relevance | greedy coverage | **MMR** |
|---|---|---|---|---|---|
| 30% | 0.6973 | 0.9272 | 0.9317 | 0.7274 | **0.9360** |
| 50% | 0.5107 | 0.8538 | 0.8563 | 0.5405 | **0.8623** |
| 70% | 0.3109 | 0.7415 | 0.7469 | 0.3493 | **0.7491** |
| 80% | 0.1999 | 0.6525 | 0.6532 | 0.2450 | **0.6664** |
| 90% | 0.1006 | 0.4976 | 0.4965 | 0.1377 | **0.5136** |

## Paired significance (2,100 questions, identical inputs per arm)

Paired bootstrap on mean support recall (20,000 resamples); McNemar exact test
on the binary full-support outcome.

| Compression | MMR − random | p | MMR − top-k | p (boot) | McNemar p |
|---|---|---|---|---|---|
| 30% | +0.2387 | <1e-300 | +0.0043 | 0.057 | 0.34 |
| 50% | +0.3516 | <1e-300 | +0.0060 | 0.037 | 0.37 |
| 70% | +0.4383 | <1e-300 | +0.0022 | 0.531 | 0.83 |
| 80% | +0.4664 | <1e-300 | +0.0131 | 0.0007 | 0.49 |
| 90% | +0.4130 | <1e-300 | +0.0171 | <1e-4 | 0.040 |

## What these numbers do and do not support

**Supported.** Embedding-based selection massively beats random pruning at every
compression level — +0.24 to +0.47 mean support recall, p far below any
threshold. At 50% compression the pipeline retains **86.2%** of required
evidence against **51.1%** for random.

**Weakly supported.** MMR beats pure top-k relevance, but by **0.2 to 1.7
percentage points**. The gap reaches conventional significance on support recall
only at 80% and 90% compression. On the stricter full-support metric it is not
significant anywhere except marginally at 90% (p=0.040), which would not survive
correction for five comparisons. The honest reading: **redundancy-aware
selection buys a small amount, and only under aggressive compression.**

**Refuted.** Pure diversity does *not* work on a query-driven task. Greedy
facility location — the spectral/coverage objective with no relevance term —
scores 0.5405 at 50% compression against random's 0.5107. It is barely better
than chance, because the most *distinct* chunk in a corpus is usually the most
*irrelevant* one. Any claim that entropy/SVD selection alone beats simple
relevance ranking is **not supported by this evaluation**.

## Cost

| Quantity | Value |
|---|---|
| Pruning | 0.18 ms per document per method |
| Embedding | 37.8 ms per document (MiniLM-L6-v2, Apple MPS) |
| Tokens saved | ~620 per query at 50% compression (1,240 → 620) |

## Reproducing

```bash
pip install -e ".[embeddings,eval,dev]"
python scripts/eval_hotpot.py --parquet <hotpot_dev_distractor.parquet> --questions 3000
cd scripts && PYTHONPATH=. python significance.py --parquet <same> --questions 3000
```

Data: `distractor/validation-00000-of-00001.parquet` from the
`hotpotqa/hotpot_qa` dataset on Hugging Face.
