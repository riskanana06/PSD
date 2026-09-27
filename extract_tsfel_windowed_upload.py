import inspect
import os
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import tsfel.feature_extraction.features as tsfel_features
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# KONFIGURASI
# ============================================================

folder_materi = Path(__file__).parent

input_file = (
    folder_materi
    / "Timeseries_CO_NO2_SO2_AsemRowo_Clean.csv"
)

output_fitur = (
    folder_materi
    / "AsemRowo_TSFEL_204_Windowed.csv"
)

output_metadata = (
    folder_materi
    / "AsemRowo_TSFEL_Window_Metadata.csv"
)

# Satu data per hari
fs = 1

# Setiap baris fitur mewakili 30 hari.
window_size = 30

# Jendela bergeser 7 hari.
step_size = 7

nama_tabel_aiven = "asemrowo_tsfel_204_windowed"


# ============================================================
# DAFTAR 68 FITUR
# ============================================================

FEATURE_LIST = """
abs_energy
auc
autocorr
average_power
calc_centroid
calc_max
calc_mean
calc_median
calc_min
calc_std
calc_var
dfa
distance
ecdf
ecdf_percentile
ecdf_percentile_count
ecdf_slope
entropy
fundamental_frequency
higuchi_fractal_dimension
hist_mode
human_range_energy
hurst_exponent
interq_range
kurtosis
lempel_ziv
lpcc
max_frequency
max_power_spectrum
maximum_fractal_length
mean_abs_deviation
mean_abs_diff
mean_diff
median_abs_deviation
median_abs_diff
median_diff
median_frequency
mfcc
mse
negative_turning
neighbourhood_peaks
petrosian_fractal_dimension
pk_pk_distance
positive_turning
power_bandwidth
rms
skewness
slope
spectral_centroid
spectral_decrease
spectral_distance
spectral_entropy
spectral_kurtosis
spectral_positive_turning
spectral_roll_off
spectral_roll_on
spectral_skewness
spectral_slope
spectral_spread
spectral_variation
spectrogram_mean_coeff
sum_abs_diff
wavelet_abs_mean
wavelet_energy
wavelet_entropy
wavelet_std
wavelet_var
zero_cross
""".split()


if len(FEATURE_LIST) != 68:
    raise ValueError(
        f"Jumlah fitur bukan 68, tetapi {len(FEATURE_LIST)}."
    )


# ============================================================
# FUNGSI EKSTRAKSI
# ============================================================

def ubah_ke_skalar(hasil):
    """
    Mengubah keluaran TSFEL yang berbentuk angka, list,
    array, tuple, atau dictionary menjadi satu nilai skalar.
    """

    if isinstance(hasil, dict) and "values" in hasil:
        hasil = hasil["values"]

    if isinstance(hasil, (list, tuple, np.ndarray)):
        array = np.asarray(hasil, dtype=float)

        if array.size == 0:
            return np.nan

        return float(np.nanmean(array))

    return float(hasil)


def ekstrak_satu_fitur(
    nama_fitur,
    sinyal,
    sampling_frequency,
):
    """
    Menjalankan satu fungsi fitur TSFEL.
    Parameter fs diberikan hanya jika diperlukan.
    """

    fungsi = getattr(
        tsfel_features,
        nama_fitur,
    )

    parameter = inspect.signature(
        fungsi
    ).parameters

    if "fs" in parameter:
        hasil = fungsi(
            sinyal,
            sampling_frequency,
        )
    else:
        hasil = fungsi(sinyal)

    return ubah_ke_skalar(hasil)


def ekstrak_satu_window(
    sinyal,
    nama_polutan,
    nomor_window,
):
    """
    Mengekstraksi 68 fitur dari satu window
    untuk satu polutan.
    """

    hasil_fitur = {}

    for nama_fitur in FEATURE_LIST:
        nama_kolom = (
            f"{nama_polutan}_{nama_fitur}"
        )

        try:
            nilai = ekstrak_satu_fitur(
                nama_fitur,
                sinyal,
                fs,
            )

            hasil_fitur[nama_kolom] = nilai

        except Exception as error:
            print(
                f"Peringatan: window {nomor_window}, "
                f"{nama_polutan}, fitur {nama_fitur} "
                f"menghasilkan error: {error}"
            )

            hasil_fitur[nama_kolom] = np.nan

    return hasil_fitur


# ============================================================
# MEMBACA DAN MEMERIKSA DATA CLEAN
# ============================================================

if not input_file.exists():
    raise FileNotFoundError(
        f"File tidak ditemukan:\n{input_file}"
    )


df = pd.read_csv(input_file)


# Menyeragamkan nama kolom.
df.columns = [
    str(kolom).strip()
    for kolom in df.columns
]


# Mencari kolom tanggal.
kolom_tanggal = None

for kolom in df.columns:
    if kolom.lower() in [
        "date",
        "tanggal",
        "time",
        "datetime",
    ]:
        kolom_tanggal = kolom
        break


if kolom_tanggal is None:
    raise ValueError(
        "Kolom tanggal tidak ditemukan."
    )


df[kolom_tanggal] = pd.to_datetime(
    df[kolom_tanggal],
    utc=True,
    errors="coerce",
)


if df[kolom_tanggal].isna().any():
    raise ValueError(
        "Masih terdapat tanggal yang tidak valid."
    )


# Mengurutkan data berdasarkan tanggal.
df = (
    df.sort_values(kolom_tanggal)
    .drop_duplicates(
        subset=[kolom_tanggal],
        keep="first",
    )
    .reset_index(drop=True)
)


polutan_list = ["CO", "NO2", "SO2"]


for polutan in polutan_list:
    if polutan not in df.columns:
        raise ValueError(
            f"Kolom {polutan} tidak ditemukan."
        )

    df[polutan] = pd.to_numeric(
        df[polutan],
        errors="coerce",
    )


print("Pemeriksaan data sebelum ekstraksi")
print("-----------------------------------")
print("Ukuran data:", df.shape)
print("Tanggal awal:", df[kolom_tanggal].min())
print("Tanggal akhir:", df[kolom_tanggal].max())

print("\nMissing value:")
print(df[polutan_list].isna().sum())

print("\nNilai negatif:")
print((df[polutan_list] < 0).sum())


if df[polutan_list].isna().any().any():
    raise ValueError(
        "Data masih memiliki missing value. "
        "Gunakan file hasil preprocessing."
    )


if (df[polutan_list] < 0).any().any():
    raise ValueError(
        "Data masih memiliki nilai negatif."
    )


if len(df) < window_size:
    raise ValueError(
        "Jumlah data lebih sedikit daripada "
        "ukuran window."
    )


# ============================================================
# EKSTRAKSI WINDOWED
# ============================================================

semua_window = []
metadata_window = []

nomor_window = 1


for posisi_awal in range(
    0,
    len(df) - window_size + 1,
    step_size,
):
    posisi_akhir = (
        posisi_awal + window_size
    )

    data_window = df.iloc[
        posisi_awal:posisi_akhir
    ]

    tanggal_awal = data_window[
        kolom_tanggal
    ].iloc[0]

    tanggal_akhir = data_window[
        kolom_tanggal
    ].iloc[-1]

    hasil_satu_window = {}

    for polutan in polutan_list:
        sinyal = (
            data_window[polutan]
            .astype(float)
            .to_numpy()
        )

        hasil_polutan = (
            ekstrak_satu_window(
                sinyal,
                polutan,
                nomor_window,
            )
        )

        hasil_satu_window.update(
            hasil_polutan
        )

    semua_window.append(
        hasil_satu_window
    )

    metadata_window.append(
        {
            "window_id": nomor_window,
            "tanggal_awal": tanggal_awal,
            "tanggal_akhir": tanggal_akhir,
            "jumlah_hari": window_size,
        }
    )

    print(
        f"Window {nomor_window} selesai: "
        f"{tanggal_awal.date()} sampai "
        f"{tanggal_akhir.date()}"
    )

    nomor_window += 1


df_fitur = pd.DataFrame(
    semua_window
)

df_metadata = pd.DataFrame(
    metadata_window
)


# ============================================================
# MEMASTIKAN URUTAN 204 KOLOM
# ============================================================

urutan_kolom = []


for polutan in polutan_list:
    for nama_fitur in FEATURE_LIST:
        urutan_kolom.append(
            f"{polutan}_{nama_fitur}"
        )


df_fitur = df_fitur[
    urutan_kolom
]


if df_fitur.shape[1] != 204:
    raise ValueError(
        "Jumlah kolom fitur tidak sesuai. "
        f"Diperoleh {df_fitur.shape[1]} kolom."
    )


# ============================================================
# MEMBERSIHKAN HASIL FITUR
# ============================================================

# Mengubah nilai infinity menjadi NaN.
df_fitur = df_fitur.replace(
    [np.inf, -np.inf],
    np.nan,
)


jumlah_missing_sebelum = int(
    df_fitur.isna().sum().sum()
)


print(
    "\nMissing/inf hasil ekstraksi sebelum "
    "pembersihan:",
    jumlah_missing_sebelum,
)


# Imputasi setiap fitur menggunakan median
# dari seluruh window.
for kolom in df_fitur.columns:
    if df_fitur[kolom].isna().any():
        nilai_median = (
            df_fitur[kolom].median()
        )

        # Jika seluruh nilai dalam satu fitur NaN,
        # fitur tersebut diisi 0.
        if pd.isna(nilai_median):
            nilai_median = 0.0

        df_fitur[kolom] = (
            df_fitur[kolom]
            .fillna(nilai_median)
        )


jumlah_missing_akhir = int(
    df_fitur.isna().sum().sum()
)

jumlah_inf_akhir = int(
    np.isinf(
        df_fitur.to_numpy(dtype=float)
    ).sum()
)


if jumlah_missing_akhir != 0:
    raise ValueError(
        "Hasil fitur masih memiliki missing value."
    )


if jumlah_inf_akhir != 0:
    raise ValueError(
        "Hasil fitur masih memiliki nilai infinity."
    )


# ============================================================
# MENYIMPAN CSV
# ============================================================

df_fitur.to_csv(
    output_fitur,
    index=False,
)

df_metadata.to_csv(
    output_metadata,
    index=False,
)


print("\nEkstraksi windowed berhasil.")
print("Ukuran fitur:", df_fitur.shape)
print("Jumlah fitur:", df_fitur.shape[1])
print("Jumlah window:", df_fitur.shape[0])
print("Missing value akhir:", jumlah_missing_akhir)
print("Infinity akhir:", jumlah_inf_akhir)
print("File fitur:", output_fitur)
print("File metadata:", output_metadata)


# ============================================================
# KONEKSI DAN UPLOAD KE AIVEN
# ============================================================

load_dotenv(
    folder_materi / ".env"
)


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


variabel_wajib = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}


variabel_kosong = [
    nama
    for nama, nilai in variabel_wajib.items()
    if not nilai
]


if variabel_kosong:
    raise ValueError(
        "Variabel berikut belum tersedia "
        "di file .env: "
        + ", ".join(variabel_kosong)
    )


password_encoded = quote_plus(
    DB_PASSWORD
)


uri = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{password_encoded}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode=require"
)


engine = create_engine(
    uri,
    pool_pre_ping=True,
)


# Data yang diunggah hanya 204 kolom fitur.
# Metadata tanggal disimpan pada CSV terpisah.
df_fitur.to_sql(
    nama_tabel_aiven,
    engine,
    schema="public",
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=10,
)


with engine.connect() as connection:
    hasil_verifikasi = pd.read_sql(
        text(
            f"""
            SELECT COUNT(*) AS jumlah_baris
            FROM public.{nama_tabel_aiven};
            """
        ),
        connection,
    )

    hasil_kolom = pd.read_sql(
        text(
            f"""
            SELECT COUNT(*) AS jumlah_kolom
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = '{nama_tabel_aiven}';
            """
        ),
        connection,
    )


engine.dispose()


print("\nUpload ke Aiven berhasil.")
print("Nama tabel:", nama_tabel_aiven)
print(
    "Jumlah baris di Aiven:",
    int(
        hasil_verifikasi.loc[
            0,
            "jumlah_baris",
        ]
    ),
)
print(
    "Jumlah kolom di Aiven:",
    int(
        hasil_kolom.loc[
            0,
            "jumlah_kolom",
        ]
    ),
)

print(
    "\nData sudah siap digunakan untuk "
    "PCA 37 komponen dan K-Means."
)