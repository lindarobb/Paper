import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import pandas as pd
from pyproj import Transformer
from pathlib import Path
import matplotlib.patheffects as path_effects
from adjustText import adjust_text

# Load raster
tif_path = Path(r"C:\Users\robbl\OneDrive - lincolnagritech.co.nz\Documents\QGIS\Selwyn\Selwyn_ScottsRd_Ortho_20210702_20cm.tif")
with rasterio.open(tif_path) as src:
    raster = src.read(1)
    transform = src.transform
    raster_crs = src.crs

# Load points
csv_path = Path(r"C:\Users\robbl\OneDrive - lincolnagritech.co.nz\Documents\QGIS\Selwyn\Paper piezos.csv")
points = pd.read_csv(csv_path)

print(points.columns)  # Check column names here
output_path = csv_path.with_suffix('.png')
# Check column names and assign x/y
print(points.columns)  # Should include 'Easting', 'Northing', 'hole_name'
points['x'] = points['Easting']
points['y'] = points['Northing']

# Plot raster and points
with rasterio.open(tif_path) as src:
    transform = src.transform
    fig, ax = plt.subplots(figsize=(10, 10))

# Plot the raster
    show(src.read([1, 2, 3]), transform=transform, ax=ax)

# Add points
    ax.scatter(points['x'], points['y'], color='red', edgecolor='black', s=40, label='Sampling Points')

    # Label points
    texts = []
    for _, row in points.iterrows():
        txt = ax.text(row['x'], row['y'], row['Hole Name'], fontsize=10, fontweight = 'bold',ha='left', va='bottom', color='black', path_effects=[path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()])
        texts.append(txt)

    adjust_text(texts, ax=ax, only_move={'points': 'y', 'text': 'y'},
                    arrowprops=dict(arrowstyle='->', color='gray'))
    # Add North arrow
    ax.annotate('N',
                xy=(0.95, 0.1), xytext=(0.95, 0.02),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center',
                fontsize=14, fontweight='bold',
                xycoords='axes fraction')
    # ✅ Add scale bar (example: 100 m)
    scale_length = 100  # in map units (meters if UTM)
    x_start = ax.get_xlim()[0] + 100
    y_start = ax.get_ylim()[0] + 100
    ax.hlines(y=y_start, xmin=x_start, xmax=x_start + scale_length, colors='black', linewidth=4)
    ax.text(x_start + scale_length / 2, y_start + 30, '100 m', ha='center', va='bottom', fontsize=10)
    ax.set_xlabel('Easting (m)')
    ax.set_ylabel('Northing (m)')
    ax.legend()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
