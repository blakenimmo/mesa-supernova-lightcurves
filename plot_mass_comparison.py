"""Poster-style comparison of bolometric light curves for the mass series.

Main panel: full light curve including the shock-breakout spike.
Inset: zoom on the first few days so the spike's shape is visible.

Usage:
    python plot_mass_comparison.py                 # 12, 14, 16, 18, 20, 22 Msun
    python plot_mass_comparison.py 12 16 20        # any subset
    python plot_mass_comparison.py --full          # show the whole post-plateau drop
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

STELLA = os.path.expanduser("~/Downloads/mesa/stella")
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
FULL = "--full" in args
masses = [a for a in args if a != "--full"] or ["12", "14", "16", "18", "20", "22"]


def find(run):
    for p in (os.path.join(HERE, "lightcurves", run, "mesa.lbol_lnuc.txt"),
              os.path.join(STELLA, f"res_{run}", "mesa.lbol_lnuc.txt")):
        if os.path.exists(p):
            return p
    sys.exit(f"Can't find light curve for {run}")


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            parts = line.replace("D", "E").split()
            try:
                rows.append([float(p) for p in parts[:2]])
            except (ValueError, IndexError):
                continue
    d = np.array(rows)
    return d[:, 0], d[:, 1]


# ordered colour ramp: light (low mass) -> dark (high mass), like the example paper
cmap = plt.get_cmap("viridis")
cols = [cmap(x) for x in np.linspace(0.88, 0.05, len(masses))]

fig, ax = plt.subplots(figsize=(8, 5.2))
if FULL:  # put the inset in the empty space under the plateau
    axin = inset_axes(ax, width="100%", height="100%", loc="lower left",
                      bbox_to_anchor=(0.25, 0.10, 0.32, 0.42), bbox_transform=ax.transAxes)
else:
    axin = inset_axes(ax, width="38%", height="44%", loc="upper right", borderpad=2.0)

for m, c in zip(masses, cols):
    run = m if m.endswith("M") else m + "M"
    t, L = load(find(run))
    lab = rf"{run[:-1]} M$_\odot$"
    ax.plot(t, L, color=c, lw=1.8, label=lab)
    axin.plot(t, L, color=c, lw=1.6)

ax.axvline(50, color="grey", ls="--", lw=1)
ymin = 36.2 if FULL else 40.5
ax.text(51.5, ymin + 0.15, "day 50", color="grey", fontsize=9)
ax.set_xlim(-5, 170)
ax.set_ylim(ymin, 45.2)
ax.set_xlabel("Days since peak bolometric luminosity")
ax.set_ylabel(r"log$_{10}$ L$_{bol}$ [erg s$^{-1}$]")
ax.set_title(r"Type IIP light curves vs initial mass (Z = 0.014, MESA + STELLA)")
ax.grid(alpha=0.25)
ax.legend(loc="lower left", bbox_to_anchor=(0.045, 0.0), fontsize=9, framealpha=1, title="Initial mass", title_fontsize=9)

# inset: shock-breakout spike and early cooling
axin.set_xlim(-0.2, 3.0)
axin.set_ylim(42.4, 45.1)
axin.set_title("Shock breakout: first 3 days", fontsize=8.5, pad=4)
axin.set_xlabel("days", fontsize=7.5, labelpad=1)
axin.tick_params(labelsize=7.5)
axin.grid(alpha=0.25)

fig.subplots_adjust(left=0.09, right=0.98, bottom=0.11, top=0.93)
tag = "_".join(m if m.endswith("M") else m + "M" for m in masses)
out = os.path.join(HERE, f"lightcurve_mass_comparison_{tag}{'_full' if FULL else ''}.png")
fig.savefig(out, dpi=250)
print(f"Saved plot to {out}")
plt.show()
