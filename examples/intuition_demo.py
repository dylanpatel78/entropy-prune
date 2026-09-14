"""Tiny numeric demos for the Module 1 concepts. Pure NumPy, no model needed."""

import numpy as np

np.set_printoptions(precision=3, suppress=True)


def show(title):
    print("\n" + "=" * 62 + f"\n{title}\n" + "=" * 62)


show("A. Cosine of two 2-D vectors, computed by hand vs numpy")
a = np.array([3.0, 4.0])
b = np.array([4.0, 3.0])
dot = float(a @ b)
na = float(np.linalg.norm(a))
nb = float(np.linalg.norm(b))
print(f"a={a}  b={b}")
print(f"dot(a,b) = 3*4 + 4*3 = {dot}")
print(f"|a| = sqrt(9+16) = {na}   |b| = sqrt(16+9) = {nb}")
print(f"cos = {dot}/({na}*{nb}) = {dot / (na * nb):.4f}")
print(f"angle = {np.degrees(np.arccos(dot / (na * nb))):.2f} degrees")

show("B. Why raw dot product is broken: the long-document problem")
query = np.array([1.0, 0.0])  # "interest rates"
exact = np.array([1.0, 0.0])  # short chunk, exactly on topic
longdoc = np.array([3.0, 9.54])  # long off-topic chunk, big norm
print(f"query   = {query}   norm={np.linalg.norm(query):.2f}")
print(f"exact   = {exact}   norm={np.linalg.norm(exact):.2f}   (short, on topic)")
print(f"longdoc = {longdoc}   norm={np.linalg.norm(longdoc):.2f}   (long, off topic)")
for name, v in [("exact", exact), ("longdoc", longdoc)]:
    d = float(query @ v)
    c = d / (np.linalg.norm(query) * np.linalg.norm(v))
    print(f"  {name:8s} raw dot = {d:6.2f}   cosine = {c:6.3f}")
print(">>> raw dot picks the WRONG one; cosine picks the right one")

show("C. The whole n^2 problem is one matrix multiply")
E = np.array([[1.0, 0.0], [0.8, 0.6], [0.0, 1.0]])
print("E (3 sentences x 2 dims), rows already unit-length:\n", E)
print("\nE.T (a free view, strides swapped, no copy):\n", E.T)
S = E @ E.T
print("\nS = E @ E.T  ->  shape", S.shape, "\n", S)
print("\nCheck one entry by hand: S[1,2] = 0.8*0.0 + 0.6*1.0 =", 0.8 * 0.0 + 0.6 * 1.0)

show("D. Eigenvalues of S == singular values of E, SQUARED")
lam = np.linalg.eigvalsh(S)[::-1]
sig = np.linalg.svd(E, compute_uv=False)
print("eigenvalues of S      :", lam)
print("singular values of E  :", sig)
print("squared              :", sig**2, " <- note only 2 nonzero: rank <= min(3,2)=2")
print("trace(S) =", S.trace(), " = n =", S.shape[0], " (always, because diagonal is 1)")

show("E. Effective rank: 'how many DIFFERENT things do I actually have?'")


def eff_rank(M, label):
    n = M.shape[0]
    lam = np.clip(np.linalg.eigvalsh(M)[::-1], 0, None)
    p = lam / lam.sum()
    H = -(p[p > 1e-12] * np.log(p[p > 1e-12])).sum()
    print(f"{label}")
    print(f"   eigenvalues = {lam}")
    print(f"   p = lam/n   = {p}")
    print(f"   H = {H:.4f} nats   effective rank = exp(H) = {np.exp(H):.3f}  (of {n})")


ident = np.eye(3)
eff_rank(ident, "3 sentences about COMPLETELY different topics (S = identity):")
dup = np.ones((3, 3))
eff_rank(dup, "\n3 IDENTICAL sentences (S = all ones):")
mixed = np.array([[1.0, 0.95, 0.1], [0.95, 1.0, 0.1], [0.1, 0.1, 1.0]])
eff_rank(mixed, "\n2 near-duplicates + 1 unrelated:")

show("F. Why a fixed threshold does not transfer (real numbers from the encoder)")
real = np.array(
    [
        [1.000, 0.584, 0.412, -0.001, -0.088],
        [0.584, 1.000, 0.422, -0.071, -0.051],
        [0.412, 0.422, 1.000, -0.120, -0.063],
        [-0.001, -0.071, -0.120, 1.000, -0.041],
        [-0.088, -0.051, -0.063, -0.041, 1.000],
    ]
)
print("The two near-duplicate Fed sentences scored 0.584.")
for t in (0.9, 0.8, 0.7, 0.5, 0.4):
    pairs = [(i, j) for i in range(5) for j in range(i + 1, 5) if real[i, j] >= t]
    print(f"  threshold {t}: catches {len(pairs)} pair(s) {pairs}")
print(
    ">>> 0.8 catches NOTHING. 0.4 catches the paraphrases too. No single number works."
)
