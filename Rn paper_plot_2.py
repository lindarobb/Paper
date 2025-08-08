import platform
from pathlib import Path
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import pandas as pd
import rasterio
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.patheffects import Stroke, Normal
import math


def plot():
    # determine root directory
    home = Path.home()
    if platform.system().startswith("Windows"):
        root = Path("Z:").joinpath("Radon")
    else:
        root = home.joinpath("mnt", "unbacked", "Radon")

    # file paths
    tif_path = root.joinpath("Selwyn_ScottsRd_Ortho_20210702_20cm.tif")
    csv_path = root.joinpath("Paper piezos.csv")
    output_path = csv_path.with_name(csv_path.stem + "_v2.png")

    # load sampling points
    df = pd.read_csv(csv_path)

    # open raster and reproject to lat/lon if needed
    with rasterio.open(tif_path) as src:
        src_crs = src.crs
        if src_crs.to_epsg() != 4326:
            dst_crs = "EPSG:4326"
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds
            )
            data = np.empty((3, height, width), dtype=src.meta["dtype"])
            for i in range(1, 4):
                reproject(
                    source=src.read(i),
                    destination=data[i - 1],
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest
                )
            img = data
            ras_transform = transform
        else:
            img = src.read([1, 2, 3])
            ras_transform = src.transform

    # fill zeros (nodata) with white
    img = np.where(img == 0, 255, img)

    # reproject points to lat/lon
    transformer = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
    df["lon"], df["lat"] = transformer.transform(
        df["Easting"].values, df["Northing"].values
    )

    # set up figure & axes
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.patch.set_edgecolor("white")
    ax.patch.set_linewidth(0)

    # show raster
    show(img, transform=ras_transform, ax=ax)

    # plot sampling points
    ax.scatter(
        df["lon"], df["lat"],
        c="red", edgecolors="black", s=40,
        label="Sampling Points"
    )

    # prepare for greedy label placement
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    offsets = [
        (0, 0),
        (5, 5), (5, -5), (-5, 5), (-5, -5),
        (10, 0), (0, 10), (-10, 0), (0, -10),
        (15, 15), (15, -15), (-15, 15), (-15, -15),
        (20, 0)
    ]
    placed_boxes = []

    # place labels without overlap
    for x, y, name in zip(df["lon"], df["lat"], df["Hole Name"]):
        placed = False
        for dx, dy in offsets:
            ann = ax.annotate(
                name,
                xy=(x, y),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=9,
                fontweight='bold',
                ha="left",
                va="bottom",
                path_effects=[Stroke(linewidth=3, foreground="white"), Normal()]
            )
            bb = ann.get_window_extent(renderer)
            if not any(bb.overlaps(other) for other in placed_boxes):
                placed_boxes.append(bb)
                placed = True
                break
            ann.remove()
        if not placed:
            dx, dy = offsets[-1]
            ax.annotate(
                name,
                xy=(x, y),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=9,
                fontweight='bold',
                ha="left",
                va="bottom",
                path_effects=[Stroke(linewidth=3, foreground="white"), Normal()]
            )

    # scale bar (~100 m in degrees)
    deg = 100 / 111000
    x0 = ax.get_xlim()[0] + deg
    y0 = ax.get_ylim()[0] + deg
    ax.hlines(y0, x0, x0 + deg, linewidth=4, color="black")
    ax.text(
        x0 + deg / 2, y0 + deg * 0.3,
        "100 m", ha="center", va="bottom", fontsize=10
    )

    # --- North arrow with true north rotation ---
    x_center = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2
    y_center = (ax.get_ylim()[0] + ax.get_ylim()[1]) / 2
    to_latlon = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
    north_point_x = x_center
    north_point_y = y_center + 10
    lon_center, lat_center = to_latlon.transform(x_center, y_center)
    lon_north, lat_north = to_latlon.transform(north_point_x, north_point_y)
    dx = lon_north - lon_center
    dy = lat_north - lat_center
    angle = math.degrees(math.atan2(dx, dy))
    arrow_length = 0.08
    ax.annotate(
        'N',
        xy=(0.95, 0.1), xytext=(0.95, 0.1 + arrow_length),
        xycoords='axes fraction',
        textcoords='axes fraction',
        arrowprops=dict(facecolor='black', width=5, headwidth=15),
        ha='center', va='center',
        fontsize=14, fontweight='bold',
        rotation=-angle
    )

    # axis labels & formatting
    ax.set(xlabel="Longitude", ylabel="Latitude")
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.tick_params(axis="x", rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()

# Run the function
plot()