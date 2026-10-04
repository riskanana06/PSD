from pathlib import Path

import geopandas as gpd
import rasterio
from shapely.geometry import box


folder = Path(__file__).parent

data = [
    {
        "kelas": "Sawah",
        "geojson": folder / "Sampel_sawah.geojson",
        "raster_folder": folder / "Sentinel2_AsemRowo_Sawah_20261004",
    },
    {
        "kelas": "Non-sawah",
        "geojson": folder / "Sampel_Non_sawah.geojson",
        "raster_folder": folder / "Sentinel2_AsemRowo_NonSawah_20261004",
    },
]


for item in data:
    print(f"\n=== {item['kelas']} ===")

    gdf = gpd.read_file(item["geojson"])
    file_tiff = sorted(item["raster_folder"].glob("*.tiff"))

    print("Jumlah polygon:", len(gdf))
    print("CRS GeoJSON:", gdf.crs)
    print("Jumlah file TIFF:", len(file_tiff))

    if len(file_tiff) != 4:
        raise ValueError(
            f"Folder {item['raster_folder'].name} "
            f"harus berisi 4 file TIFF."
        )

    for file in file_tiff:
        print("-", file.name)

    with rasterio.open(file_tiff[0]) as src:
        print("Ukuran raster:", src.width, "x", src.height)
        print("CRS raster:", src.crs)
        print("Resolusi:", src.res)
        print("Batas raster:", src.bounds)

        gdf_raster = gdf.to_crs(src.crs)
        batas_raster = box(*src.bounds)

        jumlah_berpotongan = gdf_raster.geometry.intersects(
            batas_raster
        ).sum()

        print(
            "Polygon di dalam/berpotongan dengan raster:",
            jumlah_berpotongan,
            "dari",
            len(gdf_raster),
        )

print("\nPemeriksaan data selesai.")