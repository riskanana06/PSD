import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, inspect, text


# Membaca .env yang berada di folder yang sama dengan check_db.py
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Memastikan seluruh konfigurasi tersedia
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


# URL.create aman untuk password yang memiliki karakter khusus
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


try:
    with engine.connect() as conn:
        print("Koneksi ke PostgreSQL Aiven berhasil.")

        inspector = inspect(conn)

        # Memeriksa tabel data bersih
        if inspector.has_table("no2_asemrowo_clean"):
            jumlah_data = pd.read_sql_query(
                text(
                    """
                    SELECT COUNT(*) AS jumlah_baris
                    FROM no2_asemrowo_clean
                    """
                ),
                conn,
            )

            print("\nJumlah baris data clean:")
            print(jumlah_data)
        else:
            print(
                "\nTabel no2_asemrowo_clean belum tersedia."
            )

        # Memeriksa tabel hasil ekstraksi TSFEL
        if inspector.has_table("no2_asemrowo_tsfel_68"):
            preview_fitur = pd.read_sql_query(
                text(
                    """
                    SELECT *
                    FROM no2_asemrowo_tsfel_68
                    LIMIT 5
                    """
                ),
                conn,
            )

            print("\nPreview tabel fitur TSFEL:")
            print(preview_fitur)
            print("Ukuran preview:", preview_fitur.shape)
        else:
            print(
                "Tabel no2_asemrowo_tsfel_68 belum tersedia."
            )

except Exception as error:
    print("Koneksi atau query gagal:")
    print(error)