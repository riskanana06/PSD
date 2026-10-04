from pathlib import Path

import geopandas as gpd
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import ListedColormap
from rasterio.mask import mask
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


folder = Path(__file__).parent

folder_sawah = (
    folder / "Sentinel2_AsemRowo_Sawah_20261004"
)

folder_non_sawah = (
    folder / "Sentinel2_AsemRowo_NonSawah_20261004"
)

geojson_sawah = folder / "Sampel_sawah.geojson"
geojson_non_sawah = folder / "Sampel_Non_sawah.geojson"

nama_band = ["B02", "B03", "B04", "B08"]


def cari_file_band(folder_raster, band):
    hasil = list(folder_raster.glob(f"*{band}*.tiff"))

    if len(hasil) != 1:
        raise FileNotFoundError(
            f"File {band} tidak ditemukan atau berjumlah lebih "
            f"dari satu di folder {folder_raster.name}."
        )

    return hasil[0]


def daftar_file_band(folder_raster):
    return {
        band: cari_file_band(folder_raster, band)
        for band in nama_band
    }


def rata_rata_polygon(file_raster, geometri):
    try:
        with rasterio.open(file_raster) as src:
            hasil, _ = mask(
                src,
                [geometri.__geo_interface__],
                crop=True,
                all_touched=True,
                filled=False,
            )

            nilai = hasil[0].compressed()
            nilai = nilai[np.isfinite(nilai)]

            if len(nilai) == 0:
                return np.nan

            return float(np.mean(nilai))

    except ValueError:
        return np.nan


def ekstrak_sampel(
    file_geojson,
    folder_raster,
    nama_kelas,
    kode_kelas,
):
    file_band = daftar_file_band(folder_raster)

    with rasterio.open(file_band["B02"]) as src:
        crs_raster = src.crs

    gdf = gpd.read_file(file_geojson)
    gdf = gdf.to_crs(crs_raster)

    hasil = []

    for nomor, baris in gdf.iterrows():
        geometri = baris.geometry

        nilai = {
            band: rata_rata_polygon(
                file_band[band],
                geometri,
            )
            for band in nama_band
        }

        penyebut = nilai["B08"] + nilai["B04"]

        if (
            np.isfinite(penyebut)
            and penyebut != 0
        ):
            ndvi = (
                nilai["B08"] - nilai["B04"]
            ) / penyebut
        else:
            ndvi = np.nan

        hasil.append(
            {
                "id_sampel": nomor + 1,
                "kelas": nama_kelas,
                "label": kode_kelas,
                "B02": nilai["B02"],
                "B03": nilai["B03"],
                "B04": nilai["B04"],
                "B08": nilai["B08"],
                "NDVI": ndvi,
            }
        )

    return pd.DataFrame(hasil)


print("Mengekstraksi sampel sawah...")

df_sawah = ekstrak_sampel(
    geojson_sawah,
    folder_sawah,
    "Sawah",
    1,
)

print("Mengekstraksi sampel non-sawah...")

df_non_sawah = ekstrak_sampel(
    geojson_non_sawah,
    folder_non_sawah,
    "Non-sawah",
    0,
)


df_sampel = pd.concat(
    [df_sawah, df_non_sawah],
    ignore_index=True,
)

fitur = ["B02", "B03", "B04", "B08", "NDVI"]

jumlah_awal = len(df_sampel)

df_sampel = (
    df_sampel
    .replace([np.inf, -np.inf], np.nan)
    .dropna(subset=fitur)
    .reset_index(drop=True)
)

jumlah_dihapus = jumlah_awal - len(df_sampel)

file_csv = (
    folder / "Sampel_Sentinel2_Sawah_NonSawah.csv"
)

df_sampel.to_csv(
    file_csv,
    index=False,
)


print("\nRingkasan sampel:")
print(df_sampel["kelas"].value_counts())
print("Sampel tidak valid/dihapus:", jumlah_dihapus)


X = df_sampel[fitur]
y = df_sampel["label"]

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
)


model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
)

model.fit(X_train, y_train)

y_prediksi = model.predict(X_test)

akurasi = accuracy_score(
    y_test,
    y_prediksi,
)

laporan = classification_report(
    y_test,
    y_prediksi,
    labels=[0, 1],
    target_names=["Non-sawah", "Sawah"],
    zero_division=0,
)

matriks = confusion_matrix(
    y_test,
    y_prediksi,
    labels=[0, 1],
)


print("\nAkurasi pengujian:", akurasi)
print("\nLaporan klasifikasi:")
print(laporan)
print("\nConfusion matrix:")
print(matriks)


file_laporan = (
    folder / "Laporan_Klasifikasi_Sawah_NonSawah.txt"
)

with open(
    file_laporan,
    "w",
    encoding="utf-8",
) as file:
    file.write(
        f"Akurasi: {akurasi:.6f}\n\n"
    )
    file.write(laporan)
    file.write("\nConfusion Matrix:\n")
    file.write(str(matriks))


file_model = (
    folder / "Model_RandomForest_Sawah_NonSawah.joblib"
)

joblib.dump(
    model,
    file_model,
)


display = ConfusionMatrixDisplay(
    confusion_matrix=matriks,
    display_labels=["Non-sawah", "Sawah"],
)

display.plot(
    cmap="Blues",
    values_format="d",
)

plt.title("Confusion Matrix Klasifikasi")
plt.tight_layout()

file_confusion = (
    folder / "Confusion_Matrix_Sawah_NonSawah.png"
)

plt.savefig(
    file_confusion,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


def baca_stack_raster(folder_raster):
    file_band = daftar_file_band(folder_raster)

    arrays = []
    profil = None
    transformasi = None
    crs = None

    for band in nama_band:
        with rasterio.open(file_band[band]) as src:
            data = src.read(1).astype("float32")

            if src.nodata is not None:
                data[data == src.nodata] = np.nan

            if profil is None:
                profil = src.profile.copy()
                transformasi = src.transform
                crs = src.crs
                ukuran = data.shape
            else:
                if data.shape != ukuran:
                    raise ValueError(
                        "Ukuran file raster tidak sama."
                    )

                if src.transform != transformasi:
                    raise ValueError(
                        "Transformasi raster tidak sama."
                    )

                if src.crs != crs:
                    raise ValueError(
                        "CRS raster tidak sama."
                    )

            arrays.append(data)

    b02, b03, b04, b08 = arrays

    with np.errstate(
        divide="ignore",
        invalid="ignore",
    ):
        ndvi = (
            (b08 - b04)
            / (b08 + b04)
        )

    stack = np.stack(
        [b02, b03, b04, b08, ndvi],
        axis=-1,
    )

    return stack, profil


def klasifikasi_raster(
    folder_raster,
    nama_output,
):
    stack, profil = baca_stack_raster(
        folder_raster
    )

    tinggi, lebar, jumlah_fitur = stack.shape

    data_datar = stack.reshape(
        -1,
        jumlah_fitur,
    )

    valid = np.all(
        np.isfinite(data_datar),
        axis=1,
    )

    hasil = np.full(
        data_datar.shape[0],
        255,
        dtype="uint8",
    )

    hasil[valid] = model.predict(
        data_datar[valid]
    ).astype("uint8")

    hasil = hasil.reshape(
        tinggi,
        lebar,
    )

    profil.update(
        count=1,
        dtype="uint8",
        nodata=255,
        compress="lzw",
    )

    file_output = folder / nama_output

    with rasterio.open(
        file_output,
        "w",
        **profil,
    ) as dst:
        dst.write(
            hasil,
            1,
        )

    return hasil, profil["transform"]


print("\nMembuat peta klasifikasi sawah...")

hasil_sawah, transform_sawah = klasifikasi_raster(
    folder_sawah,
    "Klasifikasi_Area_Sawah.tif",
)

print("Membuat peta klasifikasi non-sawah...")

hasil_non_sawah, transform_non_sawah = (
    klasifikasi_raster(
        folder_non_sawah,
        "Klasifikasi_Area_NonSawah.tif",
    )
)


def extent_raster(data, transformasi):
    tinggi, lebar = data.shape

    kiri = transformasi.c
    atas = transformasi.f
    kanan = kiri + lebar * transformasi.a
    bawah = atas + tinggi * transformasi.e

    return [
        kiri,
        kanan,
        bawah,
        atas,
    ]


warna = ListedColormap(
    ["#F28E2B", "#2CA02C"]
)

fig, axes = plt.subplots(
    1,
    2,
    figsize=(14, 6),
)

for ax, hasil, transformasi, judul in [
    (
        axes[0],
        hasil_sawah,
        transform_sawah,
        "Klasifikasi Area Sampel Sawah",
    ),
    (
        axes[1],
        hasil_non_sawah,
        transform_non_sawah,
        "Klasifikasi Area Sampel Non-sawah",
    ),
]:
    gambar = np.ma.masked_where(
        hasil == 255,
        hasil,
    )

    ax.imshow(
        gambar,
        cmap=warna,
        vmin=0,
        vmax=1,
        extent=extent_raster(
            hasil,
            transformasi,
        ),
    )

    ax.set_title(judul)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

plt.tight_layout()

file_peta = (
    folder / "Peta_Klasifikasi_Sawah_NonSawah.png"
)

plt.savefig(
    file_peta,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


print("\nKlasifikasi selesai.")
print("File sampel:", file_csv)
print("Model:", file_model)
print("Laporan:", file_laporan)
print("Confusion matrix:", file_confusion)
print("Peta klasifikasi:", file_peta)
print("GeoTIFF sawah: Klasifikasi_Area_Sawah.tif")
print("GeoTIFF non-sawah: Klasifikasi_Area_NonSawah.tif")