import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- load data ---
samples = pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Documents/R/Radon Paper/Selwyn Radon/Selwyn_Rn.csv").dropna()
samples = samples.query("season == 'summer' & ~site.isin(['s15','s16','s17','Riv_A2','Riv_A4','Riv_E2','Riv_C2']) & method == 'wat250'")

samples_1 = pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Documents/R/Radon Paper/Selwyn Radon/Selwyn_Rn_Depth.csv")
samples_1 = (samples_1.rename(columns={"mid":"depth"})
             .drop(columns=["winter","summer"])
             .query("~site.isin(['s15','s16','s17','Riv_A2','Riv_A4','Riv_E2','Riv_C2'])"))

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
        ax1.scatter(subset["distance"], subset["rn"]/1000, c="lightblue", marker="o", label="PG")
    elif source == "G":  # dark squares
        ax1.scatter(subset["distance"], subset["rn"]/1000, c="navy", marker="s", label="G")
    else:  # fallback
        ax1.scatter(subset["distance"], subset["rn"]/1000, label=source)

# error bars
ax1.errorbar(samples["distance"], samples["rn"]/1000,
             xerr=samples["uncertainty"], yerr=samples["sigma2"]/1000,
             fmt="none", ecolor="black", elinewidth=0.8, capsize=2)

# fit line
ax1.plot(dat["distance"], dat["rn"]/1000, "--", color="grey", lw=1)

#ax1.axhline(eqlbrm/1000, ls="--", color="grey", lw=0.5)
#ax1.text(200, eqlbrm/1000+0.2, "equilibrium", color="grey", fontsize=10, fontstyle="italic")
ax1.set_xlabel("Distance from river (m)")
ax1.set_ylabel("Rw (Bq/l)")
ax1.set_xlim(0,600)
ax1.set_ylim(0,10)
ax1.set_xticks(np.arange(0,601,100))
ax1.set_yticks(np.arange(0,11,1))
ax1.legend(title="Source")


# --- depth plot ---
initial, eqlbrm = 0.2, 18.5
dat = pd.DataFrame({"t": np.arange(1,1001)})
dat["depth"] = dat["t"]
dat["rn"] = velo(dat["t"], eqlbrm, initial)
dat["depth"] = dat["depth"] + 4  # shift

for source, subset in samples_1.groupby("source"):
    if source == "PG":
        ax2.scatter(subset["depth"], subset["rn"], c="lightblue", marker="o", label="PG")
    elif source == "G":
        ax2.scatter(subset["depth"], subset["rn"], c="navy", marker="s", label="G")
    else:
        ax2.scatter(subset["depth"], subset["rn"], label=source)

ax2.errorbar(
    samples_1["depth"], samples_1["rn"],
    xerr=[
        (samples_1["depth"] - samples_1["screen_bot"]).abs(),
        (samples_1["screen_top"] - samples_1["depth"]).abs()
    ],
    fmt="none", ecolor="black", elinewidth=0.8, capsize=2
)

ax2.plot(dat["depth"], dat["rn"], "--", color="grey", lw=1)

#ax2.axhline(eqlbrm, ls="--", color="grey", lw=0.5)
#ax2.text(22, eqlbrm+0.4, "equilibrium", color="grey", fontsize=10, fontstyle="italic")
ax2.set_xlabel("Depth (m bgl)")
ax2.set_ylabel("Rw (Bq/l)")
ax2.set_xlim(0,35)
ax2.set_ylim(0,21)
ax2.set_xticks(np.arange(0,36,5))
ax2.set_yticks(np.arange(0,22,2))
ax2.legend(title="Source", loc="upper left")

plt.tight_layout()
plt.savefig("combo_plot_py.png", dpi=300)
plt.show()
