export type Domain = "software" | "ml" | "computation" | "finance";

export type Project = {
  slug: string;
  name: string;
  domain: Domain;
  domainLabel: string;
  period: string;
  role: string;
  stack: string[];
  summary: string;
  decision: string;
  build: string;
  outcome: { value: string; label: string }[];
  spectrum: number[];
  links?: { repo?: string; demo?: string };
};

export const domainLabels: Record<Domain, string> = {
  software: "Software",
  ml: "Machine learning",
  computation: "Computation",
  finance: "Finance",
};

export const projects: Project[] = [
  {
    slug: "entropy-prune",
    name: "entropy-prune",
    domain: "ml",
    domainLabel: "Machine learning",
    period: "2025 — present",
    role: "Sole author",
    stack: ["Python", "PyTorch", "NumPy", "sentence-transformers"],
    summary:
      "Context pruning for language models, scored by Shannon entropy over an SVD subspace.",
    decision:
      "The obvious approach was a learned pruner — train a small model to predict which spans matter. I killed it. It needed labelled data nobody had, it would drift the moment the base model changed, and it turned a library into a training pipeline. Scoring spans by information content instead meant no training, no labels, and behaviour I could explain to someone in a code review.",
    build:
      "Embeds candidate spans, decomposes the embedding matrix with a truncated SVD, and scores each span by its Shannon entropy within the retained subspace, penalised by cosine similarity to spans already kept. Redundancy is the thing that actually wastes a context window, so the penalty matters more than the raw score.",
    outcome: [
      { value: "73%", label: "context removed" },
      { value: "1.9x", label: "faster prefill" },
      { value: "0.4%", label: "accuracy delta" },
    ],
    spectrum: [100, 92, 81, 74, 61, 52, 44, 33, 27, 21, 16, 12, 9, 6, 4, 3, 2],
    links: { repo: "https://github.com/example/entropy-prune" },
  },
  {
    slug: "tide",
    name: "tide",
    domain: "software",
    domainLabel: "Software",
    period: "2025",
    role: "Backend engineer",
    stack: ["Go", "Postgres", "NATS", "Docker"],
    summary:
      "An event pipeline that holds ordering guarantees without holding a global lock.",
    decision:
      "Everyone wanted exactly-once delivery. Exactly-once across a network is mostly a story people tell, and chasing it would have cost us a coordinator and a single point of failure. I argued for at-least-once with idempotent consumers, which is the same guarantee from the caller's side and about a third of the machinery.",
    build:
      "Per-key ordered partitions with a write-ahead log, consumer offsets in Postgres, and a dedupe window keyed on producer sequence numbers. Backpressure propagates rather than buffering, so a slow consumer degrades throughput instead of exhausting memory.",
    outcome: [
      { value: "12k", label: "events per second" },
      { value: "40ms", label: "p99 end to end" },
      { value: "0", label: "ordering violations in 90 days" },
    ],
    spectrum: [100, 88, 79, 68, 58, 49, 41, 30, 22, 17, 13, 9, 7, 5, 3],
  },
  {
    slug: "lattice",
    name: "lattice",
    domain: "computation",
    domainLabel: "Computation",
    period: "2024 — 2025",
    role: "Sole author",
    stack: ["C++", "CUDA", "Python bindings"],
    summary:
      "A sparse linear solver tuned for the one matrix shape that actually showed up.",
    decision:
      "I could have written a general solver. I looked at the workload first and found that 94% of the matrices were banded and diagonally dominant. Specialising for that shape and falling back to SciPy for everything else was a worse library and a much better tool.",
    build:
      "Blocked Thomas algorithm on the GPU with a shared-memory tile per band, coalesced loads, and a host-side heuristic that routes non-conforming matrices to the reference path so the fast case never has to check.",
    outcome: [
      { value: "8.4x", label: "over the SciPy baseline" },
      { value: "94%", label: "of workload on the fast path" },
    ],
    spectrum: [100, 95, 84, 77, 66, 54, 47, 38, 29, 23, 18, 14, 10, 7],
  },
  {
    slug: "basis",
    name: "basis",
    domain: "finance",
    domainLabel: "Finance",
    period: "2024",
    role: "Sole author",
    stack: ["Rust", "Polars", "Parquet"],
    summary:
      "A backtester that refuses to show you a result it cannot defend.",
    decision:
      "The tempting feature was speed — run ten thousand parameter sweeps and pick the winner. That is a machine for manufacturing overfit strategies. I built the opposite: the engine runs fewer configurations and refuses to report a Sharpe ratio without the walk-forward window and trade count sitting next to it.",
    build:
      "Columnar event replay over Parquet with point-in-time joins, so a backtest cannot see a price it would not have had. Survivorship-corrected universe, explicit slippage and borrow models, and a hard failure when a lookahead is detected rather than a warning nobody reads.",
    outcome: [
      { value: "220ms", label: "for a ten-year replay" },
      { value: "11", label: "lookahead bugs caught in review" },
    ],
    spectrum: [100, 90, 76, 70, 59, 46, 39, 31, 24, 19, 15, 11, 8],
  },
];
