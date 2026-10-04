from pathlib import Path

import numpy as np
import pandas as pd


folder = Path(__file__).parent

input_file = (
    folder
    / "Timeseries_CO_NO2_SO2_AsemRowo_Raw.csv"
)

output_linear = (
    folder
    / "Timeseries_CO_NO2_SO2_AsemRowo_Linear.csv"
)

output_polynomial = (
    folder
    / "Timeseries_CO_NO2_SO2_AsemRowo_Polynomial.csv"
)

polutan = ["CO", "NO2", "SO2"]


# Membaca data mentah
df = pd.read_csv(input_file)

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce",
)

df = (
    df
    .dropna(subset=["date"])
    .sort_values("date")
    .reset_index(drop=True)
)


# Memastikan kolom polutan berupa angka
for nama in polutan:
    df[nama] = pd.to_numeric(
        df[nama],
        errors="coerce",
    )


print("Ukuran data mentah:", df.shape)

print("\nMissing value awal:")
print(df[polutan].isna().sum())

print("\nNilai negatif awal:")
print((df[polutan] < 0).sum())


# Membuat salinan untuk penanganan awal
df_ditangani = df.copy()


# Nilai negatif dianggap tidak valid
for nama in polutan:
    df_ditangani.loc[
        df_ditangani[nama] < 0,
        nama,
    ] = np.nan


# Deteksi outlier menggunakan IQR
print("\nHasil deteksi outlier:")

for nama in polutan:
    data_valid = df_ditangani[nama].dropna()

    q1 = data_valid.quantile(0.25)
    q3 = data_valid.quantile(0.75)
    iqr = q3 - q1

    batas_bawah = q1 - (1.5 * iqr)
    batas_atas = q3 + (1.5 * iqr)

    kondisi_outlier = (
        (df_ditangani[nama] < batas_bawah)
        | (df_ditangani[nama] > batas_atas)
    )

    jumlah_outlier = kondisi_outlier.sum()

    print(
        f"{nama}: {jumlah_outlier} outlier, "
        f"batas bawah={batas_bawah:.10f}, "
        f"batas atas={batas_atas:.10f}"
    )

    # Outlier diubah menjadi missing value
    df_ditangani.loc[
        kondisi_outlier,
        nama,
    ] = np.nan


# Menjadikan tanggal sebagai index untuk interpolasi
data_index = df_ditangani.set_index("date")


# ==================================================
# INTERPOLASI LINEAR BERDASARKAN WAKTU
# ==================================================

df_linear = data_index.copy()

for nama in polutan:
    df_linear[nama] = (
        df_linear[nama]
        .interpolate(method="time")
        .ffill()
        .bfill()
        .clip(lower=0)
    )

df_linear = df_linear.reset_index()


# ==================================================
# INTERPOLASI POLYNOMIAL ORDE 2
# ==================================================

df_polynomial = data_index.copy()

for nama in polutan:
    df_polynomial[nama] = (
        df_polynomial[nama]
        .interpolate(
            method="polynomial",
            order=2,
        )
        .ffill()
        .bfill()
        .clip(lower=0)
    )

df_polynomial = df_polynomial.reset_index()


# Validasi hasil
for metode, hasil in {
    "Linear": df_linear,
    "Polynomial": df_polynomial,
}.items():

    jumlah_missing = (
        hasil[polutan]
        .isna()
        .sum()
        .sum()
    )

    jumlah_infinity = np.isinf(
        hasil[polutan].to_numpy(dtype=float)
    ).sum()

    jumlah_negatif = (
        hasil[polutan] < 0
    ).sum().sum()

    print(f"\nHasil {metode}:")
    print("Ukuran:", hasil.shape)
    print("Missing value:", jumlah_missing)
    print("Infinity:", jumlah_infinity)
    print("Nilai negatif:", jumlah_negatif)


# Menyimpan hasil
df_linear.to_csv(
    output_linear,
    index=False,
)

df_polynomial.to_csv(
    output_polynomial,
    index=False,
)


print("\nFile berhasil dibuat:")
print(output_linear)
print(output_polynomial)