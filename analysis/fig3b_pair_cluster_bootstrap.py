
import numpy as np
import pandas as pd
from pathlib import Path

# CAFM-DTA Figure 3: Pair-clustered bootstrap
# Does not modify predictions or existing figures.

ROOT = Path(__file__).resolve().parent
OFF = ROOT / "OFF_test_prediction_EVALPATH_seed1.csv"
FILM = ROOT / "FILM_test_prediction_EVALPATH_seed1.csv"

N_BOOT = 5000
SEED = 42
KEYS = [
    "Protein", "Ligand", "standard_type",
    "assay_type", "reg_truth"
]

off = pd.read_csv(OFF)
film = pd.read_csv(FILM)

assert len(off) == len(film) == 28673
assert not off.duplicated(KEYS).any()
assert not film.duplicated(KEYS).any()

data = off[KEYS + ["reg_pred"]].merge(
    film[KEYS + ["reg_pred"]],
    on=KEYS,
    how="inner",
    validate="one_to_one",
    suffixes=("_off", "_film")
)

assert len(data) == 28673

# Identify protein-ligand clusters.
pair_index = pd.MultiIndex.from_frame(
    data[["Protein", "Ligand"]]
)
codes, unique_pairs = pd.factorize(pair_index)
counts = np.bincount(codes)
multi_pair = counts > 1

y = data["reg_truth"].to_numpy(float)
o = data["reg_pred_off"].to_numpy(float)
f = data["reg_pred_film"].to_numpy(float)

# Aggregate the moments required for Pearson
# correlation within each protein-ligand pair.
n_pairs = len(unique_pairs)

columns = [
    np.ones(len(y)),
    y, y*y,
    o, o*o, o*y,
    f, f*f, f*y
]
moments = np.column_stack([
    np.bincount(codes, weights=v, minlength=n_pairs)
    for v in columns
])

def correlation(m, is_film):
    n, sy, syy = m[0], m[1], m[2]
    if is_film:
        sx, sxx, sxy = m[6], m[7], m[8]
    else:
        sx, sxx, sxy = m[3], m[4], m[5]

    numerator = n*sxy - sx*sy
    denominator = np.sqrt(
        max(n*sxx - sx*sx, 0) *
        max(n*syy - sy*sy, 0)
    )
    return numerator / denominator if denominator > 0 else np.nan

def gain(m):
    return correlation(m, True) - correlation(m, False)

rng = np.random.default_rng(SEED)
results = []

groups = {
    "All pairs": np.arange(n_pairs),
    "Multi-assay": np.flatnonzero(multi_pair),
    "Single-assay": np.flatnonzero(~multi_pair)
}

for name, ids in groups.items():
    original = gain(moments[ids].sum(axis=0))
    boot = np.empty(N_BOOT)

    for b in range(N_BOOT):
        chosen = rng.choice(ids, size=len(ids), replace=True)
        boot[b] = gain(moments[chosen].sum(axis=0))

    assert np.isfinite(boot).all()

    lo, hi = np.percentile(boot, [2.5, 97.5])
    measurement_count = int(moments[ids, 0].sum())

    results.append({
        "slice": name,
        "pairs": len(ids),
        "measurements": measurement_count,
        "pearson_gain": original,
        "CI_lower": lo,
        "CI_upper": hi,
        "bootstrap_iterations": N_BOOT
    })

result = pd.DataFrame(results)
print("\nPAIR-CLUSTERED BOOTSTRAP RESULTS")
print(result.to_string(index=False, float_format=lambda v: f"{v:.6f}"))

output = ROOT / "fig3b_pair_cluster_bootstrap_results.csv"
result.to_csv(output, index=False)
print("\nSaved:", output)
