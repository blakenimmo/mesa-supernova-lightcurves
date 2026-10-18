import os, sys
import matplotlib.pyplot as plt
import numpy as np

STELLA = os.path.expanduser("~/Downloads/mesa/stella")

# Labels for the legend/title. Add new runs here.
LABELS = {
    "12M":    r"12 M$_\odot$, Z = 0.014",
    "20M":    r"20 M$_\odot$, Z = 0.014",
    "20M_2Z": r"20 M$_\odot$, Z = 0.028",
    "20M_1.5Z": r"20 M$_\odot$, Z = 0.021",
    "16M": r"16 M$_\odot$, Z = 0.014",
    "22M": r"22 M$_\odot$, Z = 0.014",
}

# e.g. python plot_lightcurve.py 20M 20M_2Z   (plain numbers like 12 also work)
runs = [r + "M" if r.isdigit() else r for r in (sys.argv[1:] or ["12M"])]

def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            parts = line.replace("D", "E").replace("d", "e").split()
            if len(parts) < 2:
                continue
            try:
                rows.append([float(p) for p in parts[:3]])
            except ValueError:
                continue
    if not rows:
        sys.exit(f"No numeric data found in {path}")
    data = np.array(rows)
    return data[:, 0], data[:, 1]

fig, ax = plt.subplots(figsize=(8, 5))
tmin, tmax = np.inf, -np.inf

for run in runs:
    # use the copy in this repository if present, otherwise the local STELLA results
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "lightcurves", run, "mesa.lbol_lnuc.txt")
    if not os.path.exists(path):
        path = os.path.join(STELLA, f"res_{run}", "mesa.lbol_lnuc.txt")
    if not os.path.exists(path):
        sys.exit(f"Can't find {path}")
    days, logL = load(path)
    tmin, tmax = min(tmin, days.min()), max(tmax, days.max())
    label = LABELS.get(run, run)

    i_peak = np.argmax(logL)
    print(f"\n--- {run} ---")
    print(f"Read {len(days)} points from {path}")
    print(f"Time range: {days.min():.1f} to {days.max():.1f} days after peak")
    print(f"Peak log L_bol: {logL[i_peak]:.2f} erg/s")
    for d in (25, 50, 75, 100):
        if days.min() <= d <= days.max():
            print(f"log L_bol at day {d:>3}: {np.interp(d, days, logL):.2f} erg/s")

    ax.plot(days, logL, lw=1.8, label=label)

ax.axvline(100, color="grey", ls="--", lw=1, label="day 100")
ax.set_xlabel("Days since peak bolometric luminosity")
ax.set_ylabel(r"log$_{10}$ L$_{bol}$ [erg s$^{-1}$]")
if len(runs) == 1:
    ax.set_title(f"Type IIp light curve: {LABELS.get(runs[0], runs[0])} (MESA + STELLA)")
else:
    ax.set_title("Type IIp light curves (MESA + STELLA)")
ax.set_xlim(max(tmin, -5), tmax)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   f"lightcurve_{'_vs_'.join(runs)}.png")
fig.savefig(out, dpi=200)
print(f"\nSaved plot to {out}")
plt.show()
