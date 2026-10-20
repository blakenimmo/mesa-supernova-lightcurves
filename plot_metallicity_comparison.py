"""Poster-style comparison of bolometric light curves for the 20 Msun
metallicity series (Z = 0.0142, 0.021, 0.028).

Main panel: full light curve including the shock-breakout spike.
Inset: zoom on the first few days so the spike's shape is visible.

Usage:
    python plot_metallicity_comparison.py           # cropped at log L = 40.5
    python plot_metallicity_comparison.py --full    # show the whole post-plateau drop
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

STELLA = os.path.expanduser("~/Downloads/mesa/stella")
HERE = os.path.dirname(os.path.abspath(__file__))
FULL = "--full" in sys.argv[1:]

# run folder, label, colour: warm ramp, pale -> dark as metallicity increases
# (a different colour family from the mass-series plot, so the two figures are never confused)
RUNS = [
    ("20M",      r"Z = 0.0142  (Y = 0.270)", "#F2A541"),
    ("20M_1.5Z", r"Z = 0.021   (Y = 0.298)", "#D9542C"),
    ("20M_2Z",   r"Z = 0.028   (Y = 0.298)", "#7A1C3E"),
]


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


fig, ax = plt.subplots(figsize=(8, 5.2))
if FULL:  # put the inset in the empty space under the plateau
    axin = inset_axes(ax, width="100%", height="100%", loc="lower left",
                      bbox_to_anchor=(0.37, 0.13, 0.33, 0.38), bbox_transform=ax.transAxes)
else:
    axin = inset_axes(ax, width="38%", height="44%", loc="upper right", borderpad=2.0)

for run, lab, c in RUNS:
    t, L = load(find(run))
    ax.plot(t, L, color=c, lw=1.9, label=lab)
    axin.plot(t, L, color=c, lw=1.6)

ymin = 37.4 if FULL else 40.5
ax.axvline(50, color="grey", ls="--", lw=1)
ax.text(51.5, ymin + 0.15, "day 50", color="grey", fontsize=9)
ax.set_xlim(-5, 170)
ax.set_ylim(ymin, 45.2)
ax.set_xlabel("Days since peak bolometric luminosity")
ax.set_ylabel(r"log$_{10}$ L$_{bol}$ [erg s$^{-1}$]")
ax.set_title(r"Type IIP light curves vs metallicity (20 M$_\odot$, MESA + STELLA)")
ax.grid(alpha=0.25)
ax.legend(loc="lower left", bbox_to_anchor=(0.045, 0.0), fontsize=9, framealpha=1,
          title=r"20 M$_\odot$, winds off", title_fontsize=9)

axin.set_xlim(-0.2, 3.0)
axin.set_ylim(42.4, 45.1)
axin.set_title("Shock breakout: first 3 days", fontsize=8.5, pad=4)
axin.set_xlabel("days", fontsize=7.5, labelpad=1)
axin.tick_params(labelsize=7.5)
axin.grid(alpha=0.25)

fig.subplots_adjust(left=0.09, right=0.98, bottom=0.11, top=0.93)
out = os.path.join(HERE, f"lightcurve_metallicity_comparison_20M{'_full' if FULL else ''}.png")
fig.savefig(out, dpi=250)
print(f"Saved plot to {out}")
plt.show()
