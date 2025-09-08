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

# --- Filter shaken for method == "two" ---
method2 = shaken[shaken["method"] == "two"].copy()
# --- Merge datasets on well midpoint (mid) ---
merged = pd.merge(GW, method2, on="mid", suffixes=("_gw", "_m2"))
print("Shaken method2 mids:", method2["mid"].unique())
print("GW mids:", GW["mid"].unique())
print("Data types:", method2["mid"].dtype, GW["mid"].dtype)
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