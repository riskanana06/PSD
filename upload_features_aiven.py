import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


folder_materi = Path(__file__).parent
load_dotenv(folder_materi / ".env")


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


file_dan_tabel = {
    "CO_AsemRowo_TSFEL_68_Clean.csv":
        "co_asemrowo_tsfel_68",
    "NO2_AsemRowo_TSFEL_68_Clean.csv":
        "no2_asemrowo_tsfel_68",
    "SO2_AsemRowo_TSFEL_68_Clean.csv":
        "so2_asemrowo_tsfel_68",
    "AsemRowo_TSFEL_204_Clean.csv":
        "asemrowo_tsfel_204",
}


with engine.begin() as conn:
    for nama_file, nama_tabel in file_dan_tabel.items():
        file_path = folder_materi / nama_file

        df = pd.read_csv(file_path)

        # Nama kolom PostgreSQL dibuat lowercase
        df.columns = [
            kolom.lower()
            for kolom in df.columns
        ]

        if df.isna().sum().sum() != 0:
            raise ValueError(
                f"{nama_file} masih memiliki missing value."
            )

        df.to_sql(
            nama_tabel,
            conn,
            if_exists="replace",
            index=False,
        )

        print(
            f"{nama_tabel} berhasil diunggah: "
            f"{df.shape}"
        )


print("\nVerifikasi jumlah baris:")

with engine.connect() as conn:
    for nama_tabel in file_dan_tabel.values():
        query = text(
            f"""
            SELECT COUNT(*) AS jumlah_baris
            FROM {nama_tabel}
            """
        )

        hasil = pd.read_sql_query(
            query,
            conn,
        )

        print(
            nama_tabel,
            ":",
            int(hasil.loc[0, "jumlah_baris"]),
            "baris",
        )


print("\nSeluruh tabel fitur berhasil diperbarui.")