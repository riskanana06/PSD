from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# Lokasi folder materi
folder_materi = Path(__file__).parent

# Data asli gabungan
csv_path = (
    folder_materi
    / "Timeseries_CO_NO2_SO2_AsemRowo_Raw.csv"
)

# Folder gambar Jupyter Book
folder_gambar = folder_materi / "_static"
folder_gambar.mkdir(exist_ok=True)


# Pastikan CSV tersedia
if not csv_path.exists():
    raise FileNotFoundError(
        "File tidak ditemukan: "
        "Timeseries_CO_NO2_SO2_AsemRowo_Raw.csv"
    )


# Membaca data asli
df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])

polutan = ["CO", "NO2", "SO2"]

warna = {
    "CO": "#2563eb",
    "NO2": "#ea580c",
    "SO2": "#16a34a",
}


# Memeriksa kolom
kolom_hilang = [
    nama for nama in polutan
    if nama not in df.columns
]

if kolom_hilang:
    raise ValueError(
        "Kolom tidak ditemukan: "
        + ", ".join(kolom_hilang)
    )


# ==========================================
# 1. Grafik data mentah
# ==========================================

fig, axes = plt.subplots(
    3,
    1,
    figsize=(14, 11),
    sharex=True,
)

for ax, nama in zip(axes, polutan):
    ax.plot(
        df["date"],
        df[nama],
        color=warna[nama],
        linewidth=1.2,
    )

    ax.set_title(
        f"Time Series Harian {nama}"
    )

    ax.set_ylabel(
        f"Nilai {nama}"
    )

    ax.grid(
        True,
        linestyle="--",
        alpha=0.3,
    )

axes[-1].set_xlabel("Tanggal")

fig.suptitle(
    "Data Mentah Polutan Udara Kecamatan Asem Rowo\n"
    "31 Agustus 2025 – 31 Agustus 2026",
    fontsize=15,
)

plt.xticks(rotation=45)
plt.tight_layout()

output_raw = (
    folder_gambar
    / "timeseries_raw_co_no2_so2.png"
)

plt.savefig(
    output_raw,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# ==========================================
# 2. Interpolasi untuk visualisasi
# ==========================================

df_interpolasi = (
    df
    .set_index("date")
    .copy()
)

for nama in polutan:
    df_interpolasi[nama] = (
        df_interpolasi[nama]
        .interpolate(method="time")
        .ffill()
        .bfill()
    )


# ==========================================
# 3. Grafik setelah interpolasi
# ==========================================

fig, axes = plt.subplots(
    3,
    1,
    figsize=(14, 11),
    sharex=True,
)

for ax, nama in zip(axes, polutan):
    ax.plot(
        df_interpolasi.index,
        df_interpolasi[nama],
        color=warna[nama],
        linewidth=1.2,
    )

    ax.set_title(
        f"Time Series Harian {nama} "
        "Setelah Interpolasi"
    )

    ax.set_ylabel(
        f"Nilai {nama}"
    )

    ax.grid(
        True,
        linestyle="--",
        alpha=0.3,
    )

axes[-1].set_xlabel("Tanggal")

fig.suptitle(
    "Polutan Udara Kecamatan Asem Rowo "
    "Setelah Interpolasi\n"
    "31 Agustus 2025 – 31 Agustus 2026",
    fontsize=15,
)

plt.xticks(rotation=45)
plt.tight_layout()

output_interpolasi = (
    folder_gambar
    / "timeseries_interpolasi_co_no2_so2.png"
)

plt.savefig(
    output_interpolasi,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# ==========================================
# 4. Ringkasan hasil
# ==========================================

print("Grafik berhasil dibuat:")
print(output_raw)
print(output_interpolasi)

print("\nJumlah data:", len(df))

print("\nMissing value data mentah:")
print(df[polutan].isna().sum())

print("\nMissing value setelah interpolasi:")
print(df_interpolasi[polutan].isna().sum())