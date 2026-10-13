"""
Figure 5 — Interventional control (CAFM-DTA manuscript, JCIM).
Same design as the original figure (dots, dashed identity line, terracotta),
with only the required changes:
  1) within-pair read-out added (filled circles, headline; slope 1.05)
  2) original absolute read-out kept (open circles; slope 0.885)
  3) x-axis relabelled: offset injected into Ki TRAINING labels
Values: verified (seed 1; subsampled training set; 8-epoch budget).
Outputs: Fig5_intervention.pdf + .png (600 dpi)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

delta      = np.array([0.0, 0.5, 1.0, 2.0])
within     = np.array([0.0, 0.480, 1.140, 2.054])   # within-pair (1,556 pairs)
absolute   = np.array([0.0, 0.416, 0.856, 1.791])   # mean Ki prediction (7,760)

def slope_origin(x, y):
    return float((x * y).sum() / (x * x).sum())
s_w, s_a = slope_origin(delta, within), slope_origin(delta, absolute)
print(f"slopes: within-pair {s_w:.3f}, absolute {s_a:.3f}")   # 1.045, 0.885

TERRA, GREY = "#C75B2A", "#888888"
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})

fig, ax = plt.subplots(figsize=(3.6, 3.3))
xx = np.linspace(0, 2.1, 50)
ax.plot(xx, xx, ls="--", color=GREY, lw=1.2, zorder=1)
ax.text(0.62, 0.84, "identity", rotation=45, color=GREY, fontsize=8,
        ha="center", va="center")

ax.plot(xx, s_w * xx, color=TERRA, lw=0.9, zorder=2)
ax.plot(xx, s_a * xx, color=TERRA, lw=0.9, ls=(0, (1, 1.5)), zorder=2)

ax.scatter(delta, within, s=55, color=TERRA, edgecolor=TERRA, zorder=3,
           label=f"Within-pair (slope {s_w:.2f})")
ax.scatter(delta, absolute, s=55, facecolor="white", edgecolor=TERRA,
           linewidth=1.4, zorder=3, label=f"Absolute (slope {s_a:.3f})")

ax.set_xlim(-0.1, 2.15); ax.set_ylim(-0.1, 2.15)
ax.set_xticks([0, 0.5, 1.0, 1.5, 2.0]); ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_xlabel(r"Offset injected into $K_\mathrm{i}$ training labels")
ax.set_ylabel("Recovered shift in prediction")
ax.legend(loc="upper left", frameon=False, fontsize=8, handletextpad=0.3)
fig.tight_layout()
fig.savefig("Fig5_intervention.pdf", bbox_inches="tight")
fig.savefig("Fig5_intervention.png", dpi=600, bbox_inches="tight")
print("Saved Fig5_intervention.pdf and .png")
