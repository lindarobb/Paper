import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load data ---
def mods(df):
    df["ratio"] = df["water_vol"] / df["sed_mass"]
    df["em_rate"] = df["rn_raw"] * df["ratio"]
    df["em_error"] = df["sigma"] * df["ratio"]
    df["por"] = df["unit"].apply(lambda u: 0.17 if u == "G" else 0.14)
    df["fact"] = 2.65 * ((1 - df["por"]) / df["por"])
    df["rn_eqn"] = df["em_rate"] * df["fact"]
    df["error"] = df["em_error"] * df["fact"]
    return df[["method", "mid", "rn_raw", "rn_eqn", "error"]]

# Read CSVs
shaken = mods(pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Documents/R/Radon Paper/Final Rn scripts/shaken.csv"))

GW = pd.read_csv("C:/Users/robbl/OneDrive - lincolnagritech.co.nz/Documents/R/Radon Paper/Final Rn scripts/Groundwater Samples_2.csv")[["method", "mid", "rn_raw", "rn_eqn", "error"]]


# --- Merge datasets on well midpoint (mid) ---
merged = pd.merge(GW, shaken, on="mid", suffixes=("_gw", "_m2"))
# Ensure 'mid' is numeric
shaken["mid"] = pd.to_numeric(shaken["mid"], errors="coerce").round(2)
GW["mid"] = pd.to_numeric(GW["mid"], errors="coerce").round(2)

# Merge on rounded mid
merged = pd.merge(GW, shaken, on="mid", suffixes=("_gw", "_m2"))
print("Merged shape:", merged.shape)
print(merged.head())
print("Unique mids in GW not in shaken:",
      set(GW["mid"]) - set(shaken["mid"]))
print("Unique mids in shaken not in GW:",
      set(shaken["mid"]) - set(GW["mid"]))
# --- Scatter plot GW vs Method 2 ---
plt.figure(figsize=(7, 6))
sns.scatterplot(data=merged, x="rn_eqn_m2", y="rn_eqn_gw", s=80, color="navy")

# 1:1 line for reference
lims = [
    min(merged[["rn_eqn_m2", "rn_eqn_gw"]].min()) * 0.9,
    max(merged[["rn_eqn_m2", "rn_eqn_gw"]].max()) * 1.1,
]
plt.plot(lims, lims, "r--", label="1:1 line")
plt.xlabel(r"Method 2 $R_{eq}$ (Bq/L)", fontsize=12)
plt.ylabel(r"Groundwater $R_{eq}$ (Bq/L)", fontsize=12)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()