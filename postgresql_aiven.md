# PostgreSQL Aiven dan Analisis Statistik KNIME

Tahap ini mencakup penyimpanan data polutan CO, NO₂, dan SO₂ ke basis data cloud menggunakan Aiven for PostgreSQL. Data dari Aiven kemudian dibaca menggunakan KNIME untuk dianalisis melalui node Statistics.

## 1. Konfigurasi PostgreSQL Aiven

Koneksi PostgreSQL Aiven menggunakan beberapa parameter berikut:

| Parameter | Keterangan |
|---|---|
| Database | `defaultdb` |
| User | `avnadmin` |
| SSL Mode | `require` |
| Tabel time series | `timeseries_asemrowo_clean` |
| Tabel NO₂ | `no2_asemrowo_clean` |
| Tabel fitur CO | `co_asemrowo_tsfel_68` |
| Tabel fitur NO₂ | `no2_asemrowo_tsfel_68` |
| Tabel fitur SO₂ | `so2_asemrowo_tsfel_68` |
| Tabel fitur gabungan | `asemrowo_tsfel_204` |

Informasi rahasia seperti hostname, port, username, dan password disimpan di dalam file `.env`. File tersebut tidak dimasukkan ke GitHub karena sudah dicantumkan dalam `.gitignore`.

## 2. Koneksi Aiven Menggunakan Python

Berikut adalah contoh koneksi ke PostgreSQL Aiven menggunakan variabel dari file `.env`:

```python
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_uri = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

engine = create_engine(connection_uri)

with engine.connect() as connection:
    hasil = pd.read_sql(
        "SELECT COUNT(*) AS jumlah_baris "
        "FROM timeseries_asemrowo_clean;",
        connection,
    )

    print("Koneksi ke PostgreSQL Aiven berhasil.")
    print(hasil)
```

Hasil verifikasi menunjukkan bahwa tabel `timeseries_asemrowo_clean` berisi 366 baris data harian.

## 3. Alur Pengambilan Data di KNIME

Data PostgreSQL dibaca menggunakan rangkaian node berikut:

1. **PostgreSQL Connector** untuk membuat koneksi ke Aiven.
2. **DB Table Selector** untuk memilih tabel `timeseries_asemrowo_clean`.
3. **DB Reader** untuk mengubah data database menjadi tabel KNIME.
4. **Statistics** untuk menghitung statistik deskriptif CO, NO₂, dan SO₂.

Data yang masuk ke node Statistics terdiri dari:

| Kolom | Keterangan |
|---|---|
| `date` | Tanggal pengamatan |
| `co` | Nilai polutan CO |
| `no2` | Nilai polutan NO₂ |
| `so2` | Nilai polutan SO₂ |

## 4. Statistik Deskriptif pada KNIME

Node Statistics menghitung beberapa ukuran statistik untuk setiap kolom numerik.

### 4.1 Minimum

Minimum adalah nilai paling kecil dalam data.

$$
x_{\min}=\min(x_1,x_2,\ldots,x_n)
$$

### 4.2 Maximum

Maximum adalah nilai paling besar dalam data.

$$
x_{\max}=\max(x_1,x_2,\ldots,x_n)
$$

### 4.3 Mean

Mean adalah nilai rata-rata seluruh data.

$$
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
$$

### 4.4 Median

Median adalah nilai tengah setelah data diurutkan.

Untuk jumlah data ganjil:

$$
\operatorname{Median}=x_{\frac{n+1}{2}}
$$

Untuk jumlah data genap:

$$
\operatorname{Median}
=
\frac{
x_{\frac{n}{2}}+x_{\frac{n}{2}+1}
}{2}
$$

### 4.5 Sum

Sum adalah hasil penjumlahan seluruh nilai.

$$
S=\sum_{i=1}^{n}x_i
$$

### 4.6 Variance

Variance mengukur tingkat penyebaran data terhadap nilai mean.

Rumus sample variance:

$$
s^2=
\frac{
\sum_{i=1}^{n}(x_i-\bar{x})^2
}{
n-1
}
$$

### 4.7 Standard Deviation

Standard deviation atau standar deviasi adalah akar kuadrat variance.

$$
s=\sqrt{s^2}
$$

Nilai standar deviasi yang kecil menunjukkan bahwa data berada dekat dengan mean. Nilai yang besar menunjukkan bahwa data lebih menyebar.

### 4.8 Skewness

Skewness mengukur tingkat kemencengan distribusi data.

$$
\operatorname{Skewness}
=
\frac{
\frac{1}{n}
\sum_{i=1}^{n}(x_i-\bar{x})^3
}{
\sigma^3
}
$$

Interpretasinya:

- Skewness mendekati 0 menunjukkan distribusi relatif simetris.
- Skewness positif menunjukkan distribusi menceng ke kanan.
- Skewness negatif menunjukkan distribusi menceng ke kiri.

### 4.9 Kurtosis

Kurtosis mengukur keruncingan dan berat ekor distribusi data.

$$
\operatorname{Kurtosis}
=
\frac{
\frac{1}{n}
\sum_{i=1}^{n}(x_i-\bar{x})^4
}{
\sigma^4
}
$$

Kurtosis yang lebih besar menunjukkan distribusi yang lebih runcing atau memiliki ekor yang lebih berat.

### 4.10 Missing Value

Missing value menunjukkan jumlah data yang kosong.

$$
\operatorname{Missing}
=
\sum_{i=1}^{n}I(x_i\text{ kosong})
$$

Pada data hasil preprocessing, missing value CO, NO₂, dan SO₂ adalah 0.

### 4.11 Row Count

Row count menunjukkan jumlah seluruh baris data.

$$
\operatorname{RowCount}=n
$$

Data time series Asem Rowo memiliki 366 baris.

## 5. Contoh Perhitungan Manual

Digunakan contoh tiga nilai CO:

$$
x=[0.02,\ 0.03,\ 0.04]
$$

Jumlah data:

$$
n=3
$$

### 5.1 Minimum dan Maximum

$$
x_{\min}=0.02
$$

$$
x_{\max}=0.04
$$

### 5.2 Mean

$$
\bar{x}
=
\frac{0.02+0.03+0.04}{3}
$$

$$
\bar{x}=0.03
$$

### 5.3 Median

Data yang telah diurutkan adalah:

$$
[0.02,\ 0.03,\ 0.04]
$$

Nilai tengahnya adalah:

$$
\operatorname{Median}=0.03
$$

### 5.4 Sum

$$
S=0.02+0.03+0.04
$$

$$
S=0.09
$$

### 5.5 Variance

$$
s^2=
\frac{
(0.02-0.03)^2+
(0.03-0.03)^2+
(0.04-0.03)^2
}{3-1}
$$

$$
s^2=
\frac{
0.0001+0+0.0001
}{2}
$$

$$
s^2=0.0001
$$

### 5.6 Standard Deviation

$$
s=\sqrt{0.0001}
$$

$$
s=0.01
$$

### 5.7 Skewness

Data mempunyai jarak yang simetris terhadap mean:

$$
[-0.01,\ 0,\ 0.01]
$$

Jumlah pangkat tiga deviasi adalah:

$$
(-0.01)^3+0^3+(0.01)^3=0
$$

Maka:

$$
\operatorname{Skewness}=0
$$

Artinya, contoh data mempunyai distribusi yang simetris.

### 5.8 Kurtosis

Dengan menggunakan momen populasi, nilai kurtosis contoh data adalah:

$$
\operatorname{Kurtosis}=1.5
$$

Jika menggunakan excess kurtosis:

$$
\operatorname{ExcessKurtosis}=1.5-3=-1.5
$$

Perbedaan hasil kurtosis dapat terjadi karena perangkat lunak menggunakan koreksi bias atau definisi excess kurtosis yang berbeda.

### 5.9 Missing Value dan Row Count

Tidak terdapat nilai kosong sehingga:

$$
\operatorname{Missing}=0
$$

Jumlah baris adalah:

$$
\operatorname{RowCount}=3
$$

## 6. Hasil Statistik Data Polutan

Node Statistics menghasilkan tiga baris statistik, yaitu untuk CO, NO₂, dan SO₂.

Hasil yang diperoleh menunjukkan bahwa:

- Data memiliki 366 pengamatan harian.
- Missing value akhir untuk CO, NO₂, dan SO₂ adalah 0.
- Nilai minimum, maximum, mean, variance, standard deviation, skewness, dan statistik lainnya berbeda untuk setiap polutan.
- Perbedaan tersebut menunjukkan bahwa CO, NO₂, dan SO₂ mempunyai distribusi serta pola perubahan yang berbeda.

Nilai NO₂ dan SO₂ sangat kecil sehingga pada tampilan KNIME yang dibulatkan dapat terlihat sebagai 0. Nilai aslinya tetap tersimpan sebagai bilangan desimal dan bukan benar-benar nol.

## 7. Kesimpulan

Data time series CO, NO₂, dan SO₂ berhasil disimpan dalam PostgreSQL Aiven dan dibaca kembali menggunakan KNIME. Node Statistics digunakan untuk menghitung statistik deskriptif setiap polutan.

Hasil analisis menunjukkan bahwa seluruh data telah lengkap tanpa missing value dan siap digunakan untuk proses ekstraksi fitur, PCA, serta K-Means clustering.