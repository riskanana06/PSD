from pathlib import Path

import numpy as np
import pandas as pd


folder_materi = Path(__file__).parent

input_file = (
    folder_materi
    / "Timeseries_CO_NO2_SO2_AsemRowo_Raw.csv"
)

output_file = (
    folder_materi
    / "Timeseries_CO_NO2_SO2_AsemRowo_Clean.csv"
)


# Membaca data mentah
df = pd.read_csv(input_file)
df["date"] = pd.to_datetime(df["date"])

df = (
    df
    .sort_values("date")
    .set_index("date")
)

polutan = ["CO", "NO2", "SO2"]


# Menyimpan laporan preprocessing
laporan = []


for nama in polutan:
    df[nama] = pd.to_numeric(
        df[nama],
        errors="coerce",
    )

    missing_awal = int(df[nama].isna().sum())
    negatif_awal = int((df[nama] < 0).sum())

    # Nilai negatif tidak digunakan sebagai konsentrasi fisik
    if nama == "SO2":
        df.loc[df[nama] < 0, nama] = np.nan

    # Menghitung batas outlier setelah nilai negatif ditangani
    q1 = df[nama].quantile(0.25)
    q3 = df[nama].quantile(0.75)
    iqr = q3 - q1

    batas_bawah = q1 - (1.5 * iqr)
    batas_atas = q3 + (1.5 * iqr)

    mask_outlier = (
        (df[nama] < batas_bawah)
        | (df[nama] > batas_atas)
    )

    jumlah_outlier = int(mask_outlier.sum())

    # Outlier diubah menjadi missing value
    df.loc[mask_outlier, nama] = np.nan

    # Imputasi berdasarkan waktu
    df[nama] = (
        df[nama]
        .interpolate(method="time")
        .ffill()
        .bfill()
    )

    laporan.append(
        {
            "polutan": nama,
            "missing_awal": missing_awal,
            "nilai_negatif": negatif_awal,
            "outlier": jumlah_outlier,
            "batas_bawah": batas_bawah,
            "batas_atas": batas_atas,
            "missing_akhir": int(
                df[nama].isna().sum()
            ),
        }
    )


# Mengembalikan tanggal menjadi kolom
df_clean = df.reset_index()


# Validasi
if df_clean[polutan].isna().sum().sum() != 0:
    raise ValueError(
        "Preprocessing gagal: masih ada missing value."
    )

if (df_clean[polutan] < 0).sum().sum() != 0:
    raise ValueError(
        "Preprocessing gagal: masih ada nilai negatif."
    )


# Simpan CSV clean
df_clean.to_csv(
    output_file,
    index=False,
)

laporan_df = pd.DataFrame(laporan)


print("Preprocessing berhasil.")
print("Ukuran data clean:", df_clean.shape)

print("\nLaporan preprocessing:")
print(laporan_df.to_string(index=False))

print("\nMissing value akhir:")
print(df_clean[polutan].isna().sum())

print("\nNilai negatif akhir:")
print((df_clean[polutan] < 0).sum())

print("\nFile tersimpan:")
print(output_file)