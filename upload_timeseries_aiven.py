import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, inspect, text


folder_materi = Path(__file__).parent

load_dotenv(folder_materi / ".env")


# Konfigurasi Aiven
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


konfigurasi = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}

variabel_kosong = [
    nama
    for nama, nilai in konfigurasi.items()
    if not nilai
]

if variabel_kosong:
    raise ValueError(
        "Konfigurasi .env belum lengkap: "
        + ", ".join(variabel_kosong)
    )


database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
    query={"sslmode": "require"},
)

engine = create_engine(database_url)


# Membaca CSV clean
csv_path = (
    folder_materi
    / "Timeseries_CO_NO2_SO2_AsemRowo_Clean.csv"
)

df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])

# Nama kolom dibuat konsisten untuk PostgreSQL
df = df.rename(
    columns={
        "CO": "co",
        "NO2": "no2",
        "SO2": "so2",
    }
)


# Validasi sebelum upload
if df[["co", "no2", "so2"]].isna().sum().sum() != 0:
    raise ValueError(
        "Upload dibatalkan karena masih ada missing value."
    )

if (df[["co", "no2", "so2"]] < 0).sum().sum() != 0:
    raise ValueError(
        "Upload dibatalkan karena masih ada nilai negatif."
    )


with engine.begin() as conn:
    # Tabel gabungan untuk Tugas 2
    df.to_sql(
        "timeseries_asemrowo_clean",
        conn,
        if_exists="replace",
        index=False,
    )

    # Tabel khusus NO2 untuk Tugas 4
    df[["date", "no2"]].to_sql(
        "no2_asemrowo_clean",
        conn,
        if_exists="replace",
        index=False,
    )


# Verifikasi hasil upload
with engine.connect() as conn:
    jumlah_gabungan = pd.read_sql_query(
        text(
            """
            SELECT COUNT(*) AS jumlah_baris
            FROM timeseries_asemrowo_clean
            """
        ),
        conn,
    )

    jumlah_no2 = pd.read_sql_query(
        text(
            """
            SELECT COUNT(*) AS jumlah_baris
            FROM no2_asemrowo_clean
            """
        ),
        conn,
    )

    preview = pd.read_sql_query(
        text(
            """
            SELECT *
            FROM timeseries_asemrowo_clean
            ORDER BY date
            LIMIT 5
            """
        ),
        conn,
    )


print("Upload ke Aiven berhasil.")

print("\nTabel timeseries_asemrowo_clean:")
print(jumlah_gabungan)

print("\nTabel no2_asemrowo_clean:")
print(jumlah_no2)

print("\nPreview:")
print(preview)