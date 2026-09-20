# Analisis Time Series Polutan Udara

## 1. Gambaran Time Series

Analisis time series digunakan untuk melihat perubahan nilai polutan berdasarkan urutan waktu. Data yang dianalisis meliputi CO, NO₂, dan SO₂ di Kecamatan Asem Rowo selama periode 31 Agustus 2025 sampai 31 Agustus 2026.

Dataset mempunyai 366 tanggal pengamatan harian. Namun, tidak semua tanggal mempunyai nilai pengamatan satelit yang valid.

Ringkasan missing value pada data mentah adalah:

| Polutan | Jumlah Data | Data Terisi | Missing Value |
| ------- | ----------: | ----------: | ------------: |
| CO      |         366 |         199 |           167 |
| NO₂     |         366 |         191 |           175 |
| SO₂     |         366 |         225 |           141 |

## 2. Grafik Time Series Data Mentah

```{figure} _static/timeseries_raw_co_no2_so2.png
---
name: grafik-timeseries-mentah
width: 100%
---
Time series mentah CO, NO₂, dan SO₂ di Kecamatan Asem Rowo.
```

Grafik data mentah menampilkan nilai yang berasal dari hasil pengamatan Sentinel-5P. Garis pada beberapa bagian terlihat terputus karena terdapat missing value.

Garis yang terputus tidak berarti nilai polutan sama dengan nol. Kondisi tersebut menunjukkan bahwa pada tanggal tersebut tidak tersedia hasil pengamatan yang valid.

## 3. Time Series CO

CO mempunyai 199 data terisi dan 167 missing value. Nilai CO pada data mentah berada pada rentang:

* Minimum: 0.019625 pada 20 September 2025.
* Maksimum: 0.042720 pada 7 Oktober 2025.
* Rata-rata: 0.030106.
* Median: 0.030043.

Pola CO mengalami kenaikan dan penurunan sepanjang periode pengamatan. Berdasarkan metode IQR, terdapat enam nilai yang terdeteksi sebagai outlier. Nilai tersebut perlu diperiksa sebelum digunakan dalam ekstraksi fitur.

## 4. Time Series NO₂

NO₂ mempunyai 191 data terisi dan 175 missing value. Nilai NO₂ pada data mentah berada pada rentang:

* Minimum: 0.00000511 pada 2 Agustus 2026.
* Maksimum: 0.00033235 pada 23 September 2025.
* Rata-rata: 0.00005843.
* Median: 0.00005019.

NO₂ mempunyai jumlah missing value paling banyak dibandingkan CO dan SO₂. Berdasarkan metode IQR, terdapat 12 nilai yang terdeteksi sebagai outlier.

Perbedaan yang cukup besar antara nilai maksimum dan median menunjukkan adanya beberapa lonjakan nilai NO₂ pada periode tertentu.

## 5. Time Series SO₂

SO₂ mempunyai 225 data terisi dan 141 missing value. Nilai SO₂ pada data mentah berada pada rentang:

* Minimum: -0.00107618 pada 28 Juli 2026.
* Maksimum: 0.00147138 pada 10 Juni 2026.
* Rata-rata: 0.00007109.
* Median: 0.00006744.

SO₂ mempunyai tingkat kelengkapan data paling tinggi. Namun, terdapat 93 nilai negatif dan empat outlier berdasarkan metode IQR.

Nilai negatif pada produk satelit tidak langsung diartikan sebagai konsentrasi fisik negatif. Nilai tersebut dapat berkaitan dengan noise, ketidakpastian instrumen, koreksi latar belakang, atau sinyal SO₂ yang sangat rendah.

## 6. Interpolasi Missing Value

Missing value diisi menggunakan interpolasi berdasarkan waktu. Interpolasi memperkirakan nilai kosong berdasarkan nilai sebelum dan sesudah tanggal tersebut.

Apabila masih terdapat nilai kosong pada awal atau akhir periode, digunakan metode `forward fill` dan `backward fill`.

Tahapan yang digunakan adalah:

```python
df_interpolasi[nama] = (
    df_interpolasi[nama]
    .interpolate(method="time")
    .ffill()
    .bfill()
)
```

Setelah interpolasi, jumlah missing value menjadi:

| Polutan | Missing Sebelum | Missing Setelah |
| ------- | --------------: | --------------: |
| CO      |             167 |               0 |
| NO₂     |             175 |               0 |
| SO₂     |             141 |               0 |

## 7. Grafik Setelah Interpolasi

```{figure} _static/timeseries_interpolasi_co_no2_so2.png
---
name: grafik-timeseries-interpolasi
width: 100%
---
Time series CO, NO₂, dan SO₂ setelah missing value diisi menggunakan interpolasi waktu.
```

Grafik setelah interpolasi mempunyai garis yang tersambung karena seluruh tanggal telah memiliki nilai. Nilai hasil interpolasi merupakan estimasi dan harus dibedakan dari hasil pengamatan asli satelit.

Grafik ini digunakan untuk membantu melihat pola time series secara utuh. Dataset mentah tetap dipertahankan sebagai sumber data asli.

## 8. Interpretasi Awal

Berdasarkan visualisasi time series, diperoleh beberapa temuan awal:

1. Ketiga polutan mengalami perubahan nilai dari waktu ke waktu.
2. Data mentah mempunyai banyak bagian yang terputus karena missing value.
3. NO₂ mempunyai jumlah missing value paling banyak.
4. SO₂ mempunyai data terisi paling banyak, tetapi juga memiliki nilai negatif.
5. CO mempunyai rentang nilai yang lebih stabil dibandingkan NO₂ dan SO₂.
6. NO₂ dan SO₂ memperlihatkan beberapa lonjakan nilai yang perlu diperiksa sebagai kemungkinan outlier.
7. Interpolasi membuat rangkaian data lengkap, tetapi hasilnya merupakan estimasi.
8. Preprocessing diperlukan sebelum ekstraksi fitur dan clustering.

## 9. Kesimpulan

Visualisasi time series berhasil menunjukkan pola harian CO, NO₂, dan SO₂ di Kecamatan Asem Rowo selama 366 hari.

Data mentah tetap digunakan sebagai dokumentasi hasil pengamatan satelit. Data hasil interpolasi digunakan sebagai bagian dari persiapan preprocessing, tetapi deteksi dan penanganan outlier tetap perlu dilakukan sebelum ekstraksi fitur TSFEL.