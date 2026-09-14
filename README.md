# entropy-prune

**Context pruning for LLM pipelines, driven by the eigenvalue spectrum of the
embedding matrix rather than by a hand-tuned similarity threshold.**

[![CI](https://github.com/dylanpatel78/entropy-prune/actions/workflows/ci.yml/badge.svg)](https://github.com/dylanpatel78/entropy-prune/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230)](https://github.com/astral-sh/ruff)

**[→ Live interactive demo](https://dylanpatel78.github.io/entropy-prune/)** — toggle
context chunks and watch the similarity matrix, eigenvalue spectrum, and effective
rank respond in real time. Runs entirely in the browser; no backend.

**[→ Field guide](https://dylanpatel78.github.io/entropy-prune/guide.html)** — the
full theory behind every module, from vector geometry to submodular selection, with
interactive figures and self-test questions. Written to be explained out loud.

---

## The problem

Retrieval pipelines routinely stuff 30–50 chunks into a context window, and a
large share of them say the same thing. The standard fix is pairwise cosine
dedup with a hardcoded cutoff:

```python
if cosine(a, b) > 0.8:
    drop(b)
```

That cutoff is a magic constant, and it does not survive contact with reality:

- **It does not transfer.** On `all-MiniLM-L6-v2`, two genuine paraphrases —
  *"The Federal Reserve raised interest rates by 25 basis points"* and *"The Fed
  hiked rates a quarter point at its March meeting"* — score **0.544**. A `0.8`
  cutoff catches neither. Re-tune it and you have re-fit it to one encoder on one
  corpus.
- **It is not transitive.** If `cos(a,b)=0.85`, `cos(b,c)=0.85`, and
  `cos(a,c)=0.60`, which do you drop? A pairwise rule has no principled answer;
  the result depends on iteration order.
- **It is a filter, not a budget.** Real constraints are stated in tokens.
  A threshold cannot tell you how much you will keep until after it runs.

## The approach

Redundancy is a property of the **set**, not of pairs, so measure it on the set.

Embed the chunks into a matrix `E` with L2-normalized rows, so the Gram matrix
`S = E @ E.T` is exactly the pairwise cosine matrix. Because the rows are unit
length, `trace(S) = n`, so the eigenvalues of `S` sum to `n` and `p = λ/n` is a
probability distribution with no renormalization. Feed that to Shannon entropy:

```
H = -Σ pᵢ log pᵢ            effective_rank = exp(H)
```

`exp(H)` answers *"how many genuinely distinct things are in this context?"* —
a continuous count. Twenty identical chunks score **1.0**. Twenty unrelated
chunks score **20.0**. It is unitless, needs no tuning, and is invariant to
rotations of the embedding space, so it transfers across encoders where a
threshold does not.

Those same eigenvalues are the squared singular values of `E`, which is what the
SVD subspace stage consumes — the two halves of the library compute one object.

## Install

```bash
git clone https://github.com/dylanpatel78/entropy-prune.git
cd entropy-prune
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

> PyTorch has no Python 3.14 wheels yet, so the package pins `>=3.10,<3.14`.

## Quickstart

```python
import numpy as np
from entropy_prune import EmbeddingEngine, cosine_similarity_matrix, redundancy_scores

chunks = [
    "The Federal Reserve raised interest rates by 25 basis points.",
    "The Fed hiked rates a quarter point at its March meeting.",
    "The central bank increased borrowing costs this quarter.",
    "Shannon entropy measures the information content of a distribution.",
    "My dog refuses to eat anything but salmon.",
]

engine = EmbeddingEngine()            # all-MiniLM-L6-v2, auto-selects cuda/mps/cpu
matrix = engine.encode(chunks)        # -> EmbeddingMatrix, (5, 384), unit rows
S = cosine_similarity_matrix(matrix.vectors)

print(np.round(S, 3))
print("redundancy:", np.round(redundancy_scores(S), 3))
```

```
[[ 1.     0.584  0.412 -0.001 -0.088]
 [ 0.584  1.     0.422 -0.071 -0.051]
 [ 0.412  0.422  1.    -0.12  -0.063]
 [-0.001 -0.071 -0.12   1.    -0.041]
 [-0.088 -0.051 -0.063 -0.041  1.   ]]
redundancy: [ 0.226  0.221  0.163 -0.058 -0.061]
```

The three monetary-policy chunks form a visible block; the two unrelated chunks
sit near zero. `redundancy_scores` ranks each chunk by how much of its content is
already covered elsewhere in the window.

Verify the core identity yourself — the eigenvalues of `S` are the squared
singular values of `E`, and they sum to `n`:

```python
lam = np.linalg.eigvalsh(S.astype(np.float64))[::-1]
sv  = np.linalg.svd(matrix.vectors.astype(np.float64), compute_uv=False)
assert np.allclose(lam, sv**2)        # [1.974 1.052 0.943 0.619 0.411]
assert np.isclose(lam.sum(), len(chunks))
```

## Status

The library is being built module by module. **Modules 1 is complete and
tested**; the rest are specified but not yet implemented. Nothing below is
claimed to work before it is checked off.

| # | Module | Status |
|---|--------|--------|
| 1 | Embedding matrix + cosine similarity | ✅ Implemented, tested |
| 2 | SVD subspace decomposition (Eckart–Young, randomized SVD) | 🔜 Next |
| 3 | Shannon entropy & rank selection | 🔜 |
| 4 | Pruning engine (greedy / submodular selection under a token budget) | 🔜 |
| 5 | Chunking & input layer | 📋 Planned |
| 6 | Evaluation harness (compression vs. task accuracy) | 📋 Planned |
| 7 | Scale & packaging (blocked streaming, ANN, PyPI) | 📋 Planned |

A prototype of modules 3 and 4 runs in the [live demo](https://dylanpatel78.github.io/entropy-prune/)
(greedy facility-location selection, entropy, Jacobi eigensolver — implemented in
JavaScript against the real precomputed similarity matrix). Porting it to the
Python core is module 4.

## API

| Symbol | Purpose |
|---|---|
| `EmbeddingEngine(model_name, device)` | Loads a SentenceTransformers encoder once and reuses it. |
| `EmbeddingEngine.encode(texts) -> EmbeddingMatrix` | Embeds and L2-normalizes in one step. |
| `EmbeddingMatrix` | Frozen value object binding `vectors` to `texts`; validates shape, alignment, dtype. |
| `EmbeddingMatrix.select(indices)` | Row selection preserving text alignment — the pruning primitive. |
| `cosine_similarity_matrix(vectors)` | `(n, n)` cosine matrix with exact unit diagonal and enforced symmetry. |
| `redundancy_scores(S)` | Mean off-diagonal similarity per chunk (diffuse redundancy). |
| `max_similarity_scores(S)` | Nearest-neighbour similarity per chunk (exact duplication). |
| `duplicate_pairs(S, threshold)` | Upper-triangle pairs above a cutoff, ranked. |
| `l2_normalize(matrix)` | Row-wise projection onto the unit sphere, zero-safe. |

### Design notes

**Normalization happens at the boundary, not inside `cosine`.** Unit rows are the
coordinate system the library is defined in: they are what make `trace(S) = n`,
which is what makes `λ/n` a probability distribution, which is what makes the
entropy stage well-defined without a fudge factor. `EmbeddingMatrix` validates
the invariant at construction so no downstream function can receive raw vectors.

**`float32` throughout.** The encoder's own output noise is ~1e-3, so float64's
extra digits are meaningless while doubling the memory bandwidth that actually
bottlenecks the `n²d` GEMM.

**The `(n, n)` matrix is the scaling wall.** At `n = 10,000` it is 400 MB; at
`n = 100,000` it does not fit. Module 7 replaces it with blocked streaming and an
ANN neighbour graph. The spectral path avoids it entirely — randomized truncated
SVD runs on `E` directly at `O(ndk)`.

## Development

```bash
pytest -q                       # unit tests
ruff check src tests examples   # lint
ruff format src tests examples  # format
python examples/intuition_demo.py   # numeric walkthrough of every concept
python web/build.py             # rebuild the browser demo
```

Tests pin the mathematical properties directly rather than golden outputs: unit
row norms, exact unit diagonal, symmetry, range `[-1, 1]`, positive
semi-definiteness, orthogonal rows mapping to the identity, and the
`vectors`/`texts` alignment invariant.

## The demo

`web/` builds a dependency-free, single-file interactive demo. The similarity
matrix is precomputed once with the real encoder; the browser then computes
cosine submatrices, eigenvalues (cyclic Jacobi), Shannon entropy, and greedy
selection live. Any subset you select is a **principal submatrix** of the
precomputed `S`, which is why the whole page needs only 4 KB of data instead of
shipping 384-dimensional vectors.

- `web/demo.src.html` — source, with a `__DATA__` injection point
- `web/build.py` — inlines the data, emits both builds
- `docs/index.html` — standalone build, served by GitHub Pages

`guide/` builds the field guide the same way (`guide/build.py` → `docs/guide.html`).
It is a single dependency-free file with three interactive figures — a cosine
explorer, an Eckart–Young rank-truncation demo, and an effective-rank calculator —
plus collapsible self-test questions. Study progress persists per reader via
`localStorage`, upgrading to shared storage when the page is served somewhere that
provides it.

## License

MIT — see [LICENSE](LICENSE).
