# PostgreSQL Aiven

Tahap ini mencakup integrasi dan migrasi dataset polutan $\text{NO}_2$ beserta hasil 68 fitur TSFEL ke basis data relasional cloud menggunakan layanan **Aiven for PostgreSQL**.

## 1. Konfigurasi Layanan Aiven

Layanan basis data PostgreSQL terkelola (*managed database*) dikonfigurasi menggunakan parameter koneksi aman (SSL):

| Parameter | Keterangan |
| :--- | :--- |
| **Service Name** | `pg-psd-no2` |
| **Database Name** | `defaultdb` |
| **User** | `avnadmin` |
| **SSL Mode** | `require` |
| **Tabel 1** | `no2_asemrowo_clean` (Data harian deret waktu) |
| **Tabel 2** | `no2_asemrowo_tsfel_68` (Vektor 68 fitur TSFEL) |

## 2. Skrip Migrasi Data (Python)

Migrasi data dari file CSV lokal ke PostgreSQL Aiven dilakukan menggunakan pustaka `psycopg2` dan `sqlalchemy`:

```python
import pandas as pd
from sqlalchemy import create_engine

# 1. Parameter koneksi database Aiven
DB_HOST = "pg-psd-project.aivencloud.com"
DB_PORT = "12345"
DB_NAME = "defaultdb"
DB_USER = "avnadmin"
DB_PASSWORD = "YOUR_PASSWORD"

# 2. Buat string koneksi dengan SSL mode require
connection_uri = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)
engine = create_engine(connection_uri)

# 3. Baca dataset lokal
df_clean = pd.read_csv("NO2_AsemRowo_daily_clean.csv")
df_tsfel = pd.read_csv("NO2_AsemRowo_TSFEL_68.csv")

# 4. Unggah ke tabel PostgreSQL
df_clean.to_sql("no2_asemrowo_clean", engine, if_exists="replace", index=False)
df_tsfel.to_sql("no2_asemrowo_tsfel_68", engine, if_exists="replace", index=False)

print("Migrasi data ke PostgreSQL Aiven berhasil.")