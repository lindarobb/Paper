import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from adjustText import adjust_text
import os

# define folder
out_dir = r"C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/Plots"
os.makedirs(out_dir, exist_ok=True)   # make folder if it doesn't exist

# full file path
out_path = os.path.join(out_dir, "combo_plot_py.png")

# --- define sites you want to keep ---
#keep_sites = ["River", "s30", "s31", "s32", "s33", "s34", "s35", "s36", "s37","s5"]

# --- load data ---
samples = (
    pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/Selwyn_Rn.csv")
    #.dropna()
    #.query("season == 'summer' & method == 'wat250'")
)

samples_1 = (
    pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/Selwyn_Rn_Depth.csv")
    .rename(columns={"mid":"depth"})
    .drop(columns=["winter","summer"])
    #.query("site.isin(@keep_sites)")
)

# --- shared functions ---
decay = -0.181

def velo(x, eqlbrm, initial):
    return eqlbrm*(1-np.exp(decay*x)) + initial*np.exp(decay*x)

# --- distance plot ---
initial, eqlbrm = 300, 8800
dat = pd.DataFrame({"t": np.arange(1,1001)})
dat["distance"] = dat["t"]*30
dat["rn"] = velo(dat["t"], eqlbrm, initial)

fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,6))

# scatter PG vs G
for source, subset in samples.groupby("source"):
    if source == "PG":  # light circles
        ax1.scatter(subset["distance"], subset["rn"]/1000, c="deepskyblue", marker="o", label="PG")
    elif source == "G":  # dark squares
        ax1.scatter(subset["distance"], subset["rn"]/1000, c="navy", marker="s", label="G")
    else:  # fallback
        ax1.scatter(subset["distance"], subset["rn"]/1000, label=source)
# site labels

for _, row in samples.iterrows():
    ax1.text(row["distance"], row["rn"] / 1000 + 0.2, row["site"],
             fontsize=9, ha="center", va="bottom",
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2'))


# error bars
ax1.errorbar(samples["distance"], samples["rn"]/1000,
             xerr=samples["uncertainty"], yerr=samples["sigma2"]/1000,
             fmt="none", ecolor="black", elinewidth=0.8, capsize=2)

# fit line
#ax1.plot(dat["distance"], dat["rn"]/1000, "--", color="grey", lw=1)

ax1.axhline(eqlbrm/1000, color="grey", lw=0.8, dashes=(10,4))
ax1.text(200, eqlbrm/1000+0.2, "equilibrium", color="grey", fontsize=12, fontstyle="italic")
ax1.set_xlabel("Distance from river (m)", fontsize=12)
ax1.set_ylabel(r"$Rn_{w}$ (Bq/l)", fontsize=12)

ax1.set_xticks(np.arange(0,601,100))
ax1.set_yticks(np.arange(0,11,1))
ax1.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)
ax1.legend(title=None, loc="lower right")
ax1.text(0.02, 0.95, "a", transform=ax1.transAxes, fontsize=16, fontweight="bold", va="top")  # panel label

# --- depth plot ---
initial, eqlbrm = 0.2, 18.5
dat = pd.DataFrame({"t": np.arange(1,1001)})
dat["depth"] = dat["t"]
dat["rn"] = velo(dat["t"], eqlbrm, initial)
dat["depth"] = dat["depth"] + 4  # shift

for source, subset in samples_1.groupby("source"):
    if source == "PG":
        ax2.scatter(subset["depth"], subset["rn"], c="deepskyblue", marker="o", label="PG")
    elif source == "G":
        ax2.scatter(subset["depth"], subset["rn"], c="navy", marker="s", label="G")
    else:
        ax2.scatter(subset["depth"], subset["rn"], label=source)
# error bars (add yerr)
xerr = np.array([
    (samples_1["depth"] - samples_1["screen_bot"]).abs(),
    (samples_1["screen_top"] - samples_1["depth"]).abs()
])
ax2.errorbar(
    samples_1["depth"], samples_1["rn"],
    xerr=xerr, yerr=samples_1["sigma2"],
    fmt="none",  # <--- keeps it as error bars only
    ecolor="black", elinewidth=0.8, capsize=2
)
# site labels

texts = []
for _, row in samples_1.iterrows():
          ax2.text(row["depth"], row["rn"] + 0.2, row["site"],  # start at actual data point
                 fontsize=9, ha="center", va="bottom",
                 bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2'))

# Adjust positions to avoid overlaps
adjust_text(
    texts, ax=ax2,
    only_move={'points': 'xy', 'text': 'xy'},
    arrowprops=None   # remove lines
)
#ax2.plot(dat["depth"], dat["rn"], "--", color="grey", lw=1)

ax2.axhline(eqlbrm/1000, color="grey", lw=0.8, dashes=(10,4))
ax2.text(12, eqlbrm+0.4, "equilibrium", color="grey", fontsize=12, fontstyle="italic")
ax2.set_xlabel("Depth (m bgl)", fontsize=12)
ax2.set_ylabel(r"$Rn_{w}$ (Bq/l)", fontsize=12)

ax2.set_xticks(np.arange(0,36,5))
ax2.set_yticks(np.arange(0,22,2))
ax2.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

ax2.legend(title=None, loc="lower right")
ax2.text(0.02, 0.95, "b", transform=ax2.transAxes, fontsize=16, fontweight="bold", va="top")  # panel label
ax1.set_xlim(-20,500)
ax1.set_ylim(0,10.5)
ax2.set_xlim(-1,30)
ax2.set_ylim(0,22)
plt.tight_layout()
plt.savefig(out_path, dpi=300)
plt.show()
