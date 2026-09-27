# PostgreSQL Aiven dan Analisis Statistik KNIME

Tahap ini mencakup penyimpanan data polutan CO, NOâ‚‚, dan SOâ‚‚ ke basis data cloud menggunakan **Aiven for PostgreSQL**. Data dari Aiven kemudian dibaca menggunakan KNIME untuk dianalisis melalui node **Statistics**.

## 1. Konfigurasi PostgreSQL Aiven

Koneksi PostgreSQL Aiven menggunakan beberapa parameter berikut:

| Parameter | Keterangan |
|---|---|
| Database | `defaultdb` |
| User | `avnadmin` |
| SSL Mode | `require` |
| Tabel time series | `timeseries_asemrowo_clean` |
| Tabel NOâ‚‚ | `no2_asemrowo_clean` |
| Tabel fitur CO | `co_asemrowo_tsfel_68` |
| Tabel fitur NOâ‚‚ | `no2_asemrowo_tsfel_68` |
| Tabel fitur SOâ‚‚ | `so2_asemrowo_tsfel_68` |
| Tabel fitur gabungan | `asemrowo_tsfel_204` |
| Tabel fitur windowed | `asemrowo_tsfel_204_windowed` |
| Tabel fitur normalisasi | `asemrowo_tsfel_204_normalized` |
| Tabel hasil PCA | `asemrowo_pca_37` |
| Tabel evaluasi cluster | `asemrowo_evaluasi_cluster` |
| Tabel hasil cluster PCA | `asemrowo_pca37_clustered` |
| Tabel hasil cluster fitur | `asemrowo_204fitur_clustered` |
| Tabel explained variance | `asemrowo_pca_explained_variance` |

Informasi koneksi seperti hostname, port, username, dan password disimpan di dalam file `.env`. File tersebut tidak dimasukkan ke GitHub karena telah dicantumkan dalam `.gitignore`.

## 2. Koneksi Aiven Menggunakan Python

Koneksi ke PostgreSQL Aiven dibuat menggunakan pustaka SQLAlchemy, psycopg2, dan python-dotenv.

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

Hasil verifikasi menunjukkan bahwa koneksi ke PostgreSQL Aiven berhasil dan tabel `timeseries_asemrowo_clean` berisi 366 baris data harian.

## 3. Data yang Disimpan di Aiven

Beberapa kelompok data yang disimpan di PostgreSQL Aiven adalah:

## 3.1 Data Time Series

| Tabel | Jumlah Baris | Keterangan |
|---|---:|---|
| `timeseries_asemrowo_clean` | 366 | Data bersih CO, NOâ‚‚, dan SOâ‚‚ |
| `no2_asemrowo_clean` | 366 | Data bersih khusus NOâ‚‚ |

## 3.2 Data Ekstraksi Fitur

| Tabel | Ukuran Data | Keterangan |
|---|---:|---|
| `co_asemrowo_tsfel_68` | 1 Ã— 68 | Hasil ekstraksi 68 fitur CO |
| `no2_asemrowo_tsfel_68` | 1 Ã— 68 | Hasil ekstraksi 68 fitur NOâ‚‚ |
| `so2_asemrowo_tsfel_68` | 1 Ã— 68 | Hasil ekstraksi 68 fitur SOâ‚‚ |
| `asemrowo_tsfel_204` | 1 Ã— 204 | Gabungan fitur CO, NOâ‚‚, dan SOâ‚‚ |
| `asemrowo_tsfel_204_windowed` | 49 Ã— 204 | Ekstraksi fitur menggunakan sistem window |

## 3.3 Data PCA dan Clustering

| Tabel | Ukuran Data | Keterangan |
|---|---:|---|
| `asemrowo_tsfel_204_normalized` | 49 Ã— 174 | Fitur setelah low variance filter dan normalisasi |
| `asemrowo_pca_37` | 49 Ã— 37 | Hasil reduksi PCA menjadi 37 komponen |
| `asemrowo_evaluasi_cluster` | 9 Ã— 5 | Hasil evaluasi beberapa jumlah cluster |
| `asemrowo_pca37_clustered` | 49 Ã— 38 | Hasil PCA ditambah label cluster |
| `asemrowo_204fitur_clustered` | 49 Ã— 175 | Fitur normalisasi ditambah label cluster |
| `asemrowo_pca_explained_variance` | 37 Ã— 3 | Explained variance dari 37 komponen PCA |

## 4. Alur Pengambilan Data di KNIME

Data PostgreSQL dibaca menggunakan rangkaian node berikut:

1. **PostgreSQL Connector** untuk membuat koneksi ke Aiven.
2. **DB Table Selector** untuk memilih tabel `timeseries_asemrowo_clean`.
3. **DB Reader** untuk mengubah data basis data menjadi tabel KNIME.
4. **Statistics** untuk menghitung statistik deskriptif CO, NOâ‚‚, dan SOâ‚‚.

Data yang masuk ke node Statistics terdiri atas:

| Kolom | Keterangan |
|---|---|
| `date` | Tanggal pengamatan |
| `co` | Nilai polutan CO |
| `no2` | Nilai polutan NOâ‚‚ |
| `so2` | Nilai polutan SOâ‚‚ |

Kolom `date` merupakan penanda waktu, sedangkan kolom `co`, `no2`, dan `so2` merupakan kolom numerik yang dianalisis menggunakan node Statistics.

## 5. Statistik Deskriptif pada KNIME

Node Statistics menghitung beberapa ukuran statistik untuk setiap kolom numerik.

## 5.1 Minimum

Minimum merupakan nilai paling kecil dalam data.

\[
x_{\min}=\min(x_1,x_2,\ldots,x_n)
\]

## 5.2 Maximum

Maximum merupakan nilai paling besar dalam data.

\[
x_{\max}=\max(x_1,x_2,\ldots,x_n)
\]

## 5.3 Mean

Mean merupakan nilai rata-rata seluruh data.

\[
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
\]

## 5.4 Median

Median merupakan nilai tengah setelah data diurutkan.

Untuk jumlah data ganjil:

\[
\operatorname{Median}=x_{\frac{n+1}{2}}
\]

Untuk jumlah data genap:

\[
\operatorname{Median}
=
\frac{
x_{\frac{n}{2}}+x_{\frac{n}{2}+1}
}{2}
\]

## 5.5 Sum

Sum merupakan hasil penjumlahan seluruh nilai.

\[
S=\sum_{i=1}^{n}x_i
\]

## 5.6 Variance

Variance mengukur tingkat penyebaran data terhadap nilai mean.

Rumus sample variance adalah:

\[
s^2=
\frac{
\sum_{i=1}^{n}(x_i-\bar{x})^2
}{
n-1
}
\]

## 5.7 Standard Deviation

Standard deviation atau standar deviasi merupakan akar kuadrat variance.

\[
s=\sqrt{s^2}
\]

Standar deviasi yang kecil menunjukkan bahwa nilai data berada dekat dengan mean. Standar deviasi yang besar menunjukkan bahwa data lebih menyebar.

## 5.8 Skewness

Skewness mengukur tingkat kemencengan distribusi data.

\[
\operatorname{Skewness}
=
\frac{
\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^3
}{
\sigma^3
}
\]

Interpretasi skewness:

- Skewness mendekati 0 menunjukkan distribusi relatif simetris.
- Skewness positif menunjukkan distribusi menceng ke kanan.
- Skewness negatif menunjukkan distribusi menceng ke kiri.

## 5.9 Kurtosis

Kurtosis mengukur keruncingan dan berat ekor distribusi data.

\[
\operatorname{Kurtosis}
=
\frac{
\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^4
}{
\sigma^4
}
\]

Kurtosis yang lebih besar menunjukkan distribusi yang lebih runcing atau mempunyai ekor yang lebih berat.

## 5.10 Missing Value

Missing value menunjukkan jumlah data yang kosong.

\[
\operatorname{Missing}
=
\sum_{i=1}^{n}I(x_i\text{ kosong})
\]

Pada data hasil preprocessing, missing value CO, NOâ‚‚, dan SOâ‚‚ adalah 0.

## 5.11 Row Count

Row count menunjukkan jumlah seluruh baris data.

\[
\operatorname{RowCount}=n
\]

Data time series Asem Rowo mempunyai 366 baris.

## 6. Contoh Perhitungan Manual

Contoh perhitungan menggunakan tiga nilai CO berikut:

\[
x=[0.02,\ 0.03,\ 0.04]
\]

Jumlah data:

\[
n=3
\]

## 6.1 Minimum dan Maximum

\[
x_{\min}=0.02
\]

\[
x_{\max}=0.04
\]

## 6.2 Mean

\[
\bar{x}
=
\frac{0.02+0.03+0.04}{3}
\]

\[
\bar{x}=0.03
\]

## 6.3 Median

Data yang telah diurutkan adalah:

\[
[0.02,\ 0.03,\ 0.04]
\]

Nilai tengahnya adalah:

\[
\operatorname{Median}=0.03
\]

## 6.4 Sum

\[
S=0.02+0.03+0.04
\]

\[
S=0.09
\]

## 6.5 Variance

\[
s^2=
\frac{
(0.02-0.03)^2+
(0.03-0.03)^2+
(0.04-0.03)^2
}{3-1}
\]

\[
s^2=
\frac{
0.0001+0+0.0001
}{2}
\]

\[
s^2=0.0001
\]

## 6.6 Standard Deviation

\[
s=\sqrt{0.0001}
\]

\[
s=0.01
\]

## 6.7 Skewness

Data mempunyai jarak yang simetris terhadap mean:

\[
[-0.01,\ 0,\ 0.01]
\]

Jumlah pangkat tiga deviasi adalah:

\[
(-0.01)^3+0^3+(0.01)^3=0
\]

Maka:

\[
\operatorname{Skewness}=0
\]

Artinya, contoh data mempunyai distribusi yang simetris.

## 6.8 Kurtosis

Dengan menggunakan momen populasi, nilai kurtosis contoh data adalah:

\[
\operatorname{Kurtosis}=1.5
\]

Jika menggunakan excess kurtosis:

\[
\operatorname{ExcessKurtosis}=1.5-3=-1.5
\]

Perbedaan hasil kurtosis dapat terjadi karena perangkat lunak dapat menggunakan koreksi bias atau definisi excess kurtosis yang berbeda.

## 6.9 Missing Value dan Row Count

Tidak terdapat nilai kosong sehingga:

\[
\operatorname{Missing}=0
\]

Jumlah baris adalah:

\[
\operatorname{RowCount}=3
\]

## 7. Hasil Statistik Data Polutan

Node Statistics menghasilkan tiga baris statistik, yaitu untuk CO, NOâ‚‚, dan SOâ‚‚.

Hasil yang diperoleh menunjukkan bahwa:

- Data mempunyai 366 pengamatan harian.
- Missing value akhir CO, NOâ‚‚, dan SOâ‚‚ adalah 0.
- Nilai minimum, maximum, mean, variance, standard deviation, skewness, dan statistik lainnya berbeda untuk setiap polutan.
- Perbedaan tersebut menunjukkan bahwa CO, NOâ‚‚, dan SOâ‚‚ mempunyai distribusi serta pola perubahan yang berbeda.

Nilai NOâ‚‚ dan SOâ‚‚ sangat kecil sehingga pada tampilan KNIME yang dibulatkan dapat terlihat sebagai 0. Nilai aslinya tetap tersimpan sebagai bilangan desimal dan bukan benar-benar bernilai nol.

## 8. Keamanan Informasi Koneksi

Informasi koneksi basis data tidak ditulis secara langsung di dalam kode atau website. Nilai berikut disimpan di dalam file `.env`:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

File `.env` dicantumkan dalam `.gitignore` agar password dan informasi koneksi tidak ikut diunggah ke GitHub.

## 9. Kesimpulan

Data time series CO, NOâ‚‚, dan SOâ‚‚ berhasil disimpan dalam PostgreSQL Aiven dan dibaca kembali menggunakan KNIME. Node Statistics digunakan untuk menghitung statistik deskriptif setiap polutan.

Hasil verifikasi menunjukkan bahwa data time series mempunyai 366 baris tanpa missing value. Hasil ekstraksi TSFEL, data windowed, data normalisasi, PCA, dan clustering juga telah disimpan ke dalam tabel basis data.

Dengan demikian, integrasi data lokal, PostgreSQL Aiven, Python, dan KNIME telah berhasil dilakukan.