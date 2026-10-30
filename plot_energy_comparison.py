"""Poster-style comparison of bolometric light curves for the 20 Msun
explosion-energy series (Z = 0.0142, winds off).

Main panel: full light curve including the shock-breakout spike.
Inset: zoom on the first few days so the spike's shape is visible.
Add more energies by adding lines to RUNS (folder suffix, label, colour).

Usage:
    python plot_energy_comparison.py           # cropped at log L = 40.5
    python plot_energy_comparison.py --full    # show the whole post-plateau drop
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

STELLA = os.environ.get("STELLA_DIR", os.path.expanduser("~/Downloads/mesa/stella"))
HERE = os.path.dirname(os.path.abspath(__file__))
FULL = "--full" in sys.argv[1:]

# run folder, label, colour: cool blue-green ramp, pale -> dark as energy increases
# (different colour family from the mass and metallicity plots)
RUNS = [
    ("20M_E0.6", r"E = 0.6 $\times 10^{51}$ erg",            "#A6E0CC"),
    ("20M",      r"E = 0.8 $\times 10^{51}$ erg (fiducial)", "#5CB8B8"),
    ("20M_E1.0", r"E = 1.0 $\times 10^{51}$ erg",            "#2F8AA8"),
    ("20M_E1.2", r"E = 1.2 $\times 10^{51}$ erg",            "#245A8C"),
    ("20M_E1.4", r"E = 1.4 $\times 10^{51}$ erg",            "#16264F"),
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
    # summary numbers: luminosity at day 50, day log L falls to 42 (interpolated)
    L50 = np.interp(50, t, L)
    i = np.where((L > 42) & (t > 5))[0].max()
    end = t[i] + (42 - L[i]) * (t[i + 1] - t[i]) / (L[i + 1] - L[i])
    print(f"{run:10s}  log L(day 50) = {L50:.3f}   plateau end (log L = 42) = day {end:.1f}")

ymin = 37.4 if FULL else 40.5
ax.axvline(50, color="grey", ls="--", lw=1)
ax.text(51.5, 44.95, "day 50", color="grey", fontsize=9)
ax.set_xlim(-5, 170)
ax.set_ylim(ymin, 45.2)
ax.set_xlabel("Days since peak bolometric luminosity")
ax.set_ylabel(r"log$_{10}$ L$_{bol}$ [erg s$^{-1}$]")
ax.set_title(r"Type IIP light curves vs explosion energy (20 M$_\odot$, MESA + STELLA)")
ax.grid(alpha=0.25)
ax.legend(loc="lower left", bbox_to_anchor=(0.045, 0.0), fontsize=9, framealpha=1,
          title=r"20 M$_\odot$, Z = 0.0142, winds off", title_fontsize=9)

axin.set_xlim(-0.2, 3.0)
axin.set_ylim(42.4, 45.1)
axin.set_title("Shock breakout: first 3 days", fontsize=8.5, pad=4)
axin.set_xlabel("days", fontsize=7.5, labelpad=1)
axin.tick_params(labelsize=7.5)
axin.grid(alpha=0.25)

fig.subplots_adjust(left=0.09, right=0.98, bottom=0.11, top=0.93)
out = os.path.join(HERE, f"lightcurve_energy_comparison_20M{'_full' if FULL else ''}.png")
fig.savefig(out, dpi=250)
print(f"Saved plot to {out}")
plt.show()
