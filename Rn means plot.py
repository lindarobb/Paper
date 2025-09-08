import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import os

# --- Set up plotting style ---
sns.set_style("ticks")  # cleaner look

# --- Output folder ---
out_dir = r"C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/Plots"
os.makedirs(out_dir, exist_ok=True)   # make folder if it doesn't exist

# full file path
out_path = os.path.join(out_dir, "Rn_and_Em_means_and_medians_3.png")

# --- Load data ---
def funks(name):
    levels = ["35_29.8m", "31_26.1m", "31_8.5m", "5_6.8m", "33_5.2m", "32_5.3m",
              "36_4m", "34_3.9m", "30_3.8m", "34_3.5m", "36_3.4m",
              "30_3.3m", "35_2.3m", "32_1m", "32_0.3m"]
    return pd.Categorical(name, categories=levels, ordered=True)

lambda_val = 1.81

def mods(df):
    df["ratio"] = df["water_vol"] / df["sed_mass"]
    df["em_rate"] = df["rn_raw"] * df["ratio"]
    df["em_error"] = df["sigma"] * df["ratio"]
    df["por"] = np.where(df["unit"] == "G", 0.17, 0.14)
    df["fact"] = 2.65 * ((1 - df["por"]) / df["por"])
    df["rn_eqn"] = df["em_rate"] * df["fact"]
    df["error"] = df["em_error"] * df["fact"]
    df["name"] = funks(df["name"])
    return df[["method", "name", "unit", "rn_raw", "em_rate", "em_error", "rn_eqn", "error"]]

# --- Read files (adjust paths to your data) ---
out_dir = r"C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/Plots"
pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/Selwyn_Rn.csv")
data_500 = mods(pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/500ml.csv"))
shaken = mods(pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/shaken.csv"))
BB = mods(pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/big_bottle.csv"))


dry_boxes = pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Rn paper/dry_box.csv")
dry_boxes["name"] = funks(dry_boxes["name"])
dry_boxes["rn_emission"] = dry_boxes["rn_raw"] * dry_boxes["air_vol"]
dry_boxes["em_rate"] = dry_boxes["rn_emission"] / dry_boxes["sed_mass"]
dry_boxes["em_error"] = dry_boxes["em_rate"].std(skipna=True)
dry_boxes["coeff"] = -0.13913 * np.log(dry_boxes["temp"]) + 0.676
dry_boxes["rn_wet_sed"] = dry_boxes["em_rate"] * dry_boxes["coeff"]
dry_boxes["por"] = np.where(dry_boxes["unit"] == "G", 0.17, 0.14)
dry_boxes["fact"] = 2.65 * ((1 - dry_boxes["por"]) / dry_boxes["por"])
dry_boxes["rn_eqn"] = dry_boxes["rn_wet_sed"] * dry_boxes["fact"]
dry_boxes["error"] = dry_boxes["sigma"] / dry_boxes["sed_mass"]
dry_boxes = dry_boxes[["method", "name", "unit", "rn_raw", "em_rate", "em_error", "rn_eqn", "error"]]

# --- Combine data ---
combo = pd.concat([dry_boxes, data_500, BB, shaken], ignore_index=True)

# --- Means and SDs ---
means = (
    combo.assign(rn_eqn=np.log(combo["rn_eqn"]))  # take log
         .groupby(["method", "unit"])
         .agg(mean=("rn_eqn", "mean"), STdv=("rn_eqn", "std"))  # mean + sd of log
         .reset_index()
)
# exponentiate the mean to get geometric mean
means["mean"] = np.exp(means["mean"])

stats = (
    combo.assign(em_rate =np.log(combo["em_rate"]))  # take log
         .groupby(["method", "unit"])
         .agg(mean=("em_rate", "mean"), STdv=("em_rate", "std"))  # mean + sd of log
         .reset_index()
)

stats["mean"] = np.exp(stats["mean"])

# Helper: map method+unit to dodge positions
#def get_xpos(method, unit, methods, units):
 #   """Return x-position for a given method + unit in a dodged seaborn boxplot"""
  #  base = methods.index(method)
   # n_units = len(units)
    #width = 0.8   # total box width
    #dodge = width / n_units
    #if unit == units[0]:  # e.g. G
     #   return base - dodge/2
    #else:                 # e.g. PG
     #   return base + dodge/2

methods = list(combo["method"].unique())
units = list(combo["unit"].unique())  # should be ["G", "PG"]
mpl.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 12,
    "axes.labelsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "legend.title_fontsize": 12
})

# --- Combined plot: Em (LHS) and Rn_eqn (RHS) ---
sns.set_style("whitegrid")
fig, (ax2, ax1) = plt.subplots(1, 2, figsize=(15, 6),sharex=False)

# --- Plot 2: Em_rate (left) ---
sns.boxplot(
    data=combo, x="method", y="em_rate", hue="unit",
    palette={"G": "navy", "PG": "deepskyblue"},
    fliersize=2, width=0.5, ax=ax2
)

# Add black triangles (means) centered in each box
width = 0.8  # matches seaborn default for boxplot
n_units = len(units)
dodge = width / n_units
#for _, row in stats.iterrows():
#    method_index = methods.index(row["method"])
#    unit_index = units.index(row["unit"])
#    # center of the group + offset for this unit
#    xpos = method_index + (unit_index - (n_units-1)/2) * dodge
#    ax2.scatter(xpos, row["mean"], marker="^", s=100, color="black", zorder=5)


ax2.set_ylabel(r"$E_m$ (Bq/kg)")
ax2.set_xlabel("")
ax2.set_ylim(0, 7.5)
ax2.legend_.remove()


# --- Plot 1: Rn_eqn (right) ---
sns.boxplot(
    data=combo, x="method", y="rn_eqn", hue="unit",
    palette={"G": "navy", "PG": "deepskyblue"},
    fliersize=2, width=0.5, ax=ax1
)

#for _, row in means.iterrows():
#    method_index = methods.index(row["method"])
#    unit_index = units.index(row["unit"])
#    xpos = method_index + (unit_index - (n_units-1)/2) * dodge
#    ax1.scatter(xpos, row["mean"], marker="^", s=100, color="black", zorder=5)


ax1.set_ylabel(r"$R_{eq}$ (Bq/L)")
ax1.set_xlabel("")
ax1.set_ylim(0, 100)
ax1.legend(title="Unit", loc="upper right")
plt.tight_layout()
plt.savefig(out_path, dpi=300)
plt.show()
plt.close()
