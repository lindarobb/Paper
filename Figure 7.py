import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#file_path = Path(r"C:\Users\robbl\OneDrive - lincolnagritech.co.nz\Documents\R\Radon Paper\Final Rn scripts\grain_size.csv")
# Read CSV
grain_size = pd.read_csv(r"C:\Users\robbl\OneDrive - lincolnagritech.co.nz\Documents\R\Radon Paper\Final Rn scripts\grain_size_results.csv")
output_path = r"C:\Users\robbl\OneDrive - lincolnagritech.co.nz\Documents\R\Radon Paper\Final Rn scripts\grain_size_plot.png"
# Ensure 'depth' is categorical and keeps original order
grain_size['depth'] = pd.Categorical(grain_size['depth'], categories=grain_size['depth'].unique(), ordered=True)

# Create new columns
grain_size['ratio'] = grain_size['water_vol'] / grain_size['sed_mass']
grain_size['em_rate'] = grain_size['rn_water'] * grain_size['ratio']
grain_size['em_error'] = grain_size['rn_error'] * grain_size['ratio']

gsize_order = ["<0.063", "0.063", "0.125", "0.25", "0.5", "1", "2", "4", "bulk"]

# Clean and set categorical order BEFORE grouping
grain_size['gsize'] = grain_size['gsize'].str.strip()
grain_size['gsize'] = pd.Categorical(grain_size['gsize'], categories=gsize_order, ordered=True)

# Now group and aggregate
averages = (
    grain_size
    .groupby(['gsize', 'depth'], observed=False)
    .agg(
        avg_Rn_water=('rn_water', 'mean'),
        avg_Rn_error=('rn_error', 'mean'),
        mean_em_rate=('em_rate', 'mean'),
        min_em_rate=('em_rate', 'min'),
        max_em_rate=('em_rate', 'max')
    )
    .reset_index()
)

# (Optional) Set categorical order in averages if needed
averages['gsize'] = pd.Categorical(averages['gsize'], categories=gsize_order, ordered=True)
# Plot
g = sns.FacetGrid(averages, row="depth", sharey=False, height=2.5, aspect=2)

def facet_scatter(data, color, **kwargs):
    plt.errorbar(
        data['avg_Rn_water'], data['gsize'],
        xerr=data['avg_Rn_error'],
        fmt='o', color="red", ecolor="black", elinewidth=1, capsize=3
    )

g.map_dataframe(facet_scatter)

g.set_axis_labels("", "")  # Remove global axis labels
g.set_titles("")  # Remove facet titles

for i, ax in enumerate(g.axes.flat):
    ax.tick_params(axis='x', labelrotation=0)
    ax.set_ylabel(f"Depth: {g.row_names[i]}", fontsize=10, fontweight='bold')
    # Set x-label only for the bottom facet
    if i == len(g.axes.flat) - 1:
        ax.set_xlabel("Rw (Bq/L)")
    else:
        ax.set_xlabel("")

# Add a single y-label to the figure
g.fig.text(0.04, 0.5, "Grain size of sediment samples (mm)", va='center', rotation='vertical', fontsize=12)

plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()