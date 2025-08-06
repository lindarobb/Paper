import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import pandas as pd
from pyproj import Transformer
from pathlib import Path
import matplotlib.patheffects as path_effects

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
    for _, row in points.iterrows():
        ax.text(row['x']+2, row['y']+5, row['Hole Name'], fontsize=10, fontweight = 'bold',ha='left', va='bottom', color='black', path_effects=[path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()])

    ax.set_xlabel('Easting (m)')
    ax.set_ylabel('Northing (m)')
    ax.legend()
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.show()
