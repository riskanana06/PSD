# Ekstraksi Fitur dan Clustering

## 1. Pengambilan Data

Data yang digunakan merupakan hasil ekstraksi fitur dari tiga jenis polutan, yaitu CO, NO₂, dan SO₂. Setiap polutan menghasilkan 68 fitur TSFEL sehingga total fitur setiap data adalah:

$$
68 \times 3 = 204 \text{ fitur}
$$

Terdapat dua dataset berdasarkan metode penanganan missing value dan outlier, yaitu:

1. Dataset hasil interpolasi linear.
2. Dataset hasil interpolasi polynomial.

Data seluruh mahasiswa disimpan pada database MySQL dalam dua tabel:

- `ekstraksi_fitur_linier`
- `ekstraksi_fitur_polynomial`

Data diambil dari MySQL menggunakan node **MySQL Connector** dan **DB Query Reader** pada KNIME.

Setelah data diperiksa dan disesuaikan, dataset yang digunakan dalam proses clustering terdiri atas **37 baris data mahasiswa**. Setiap baris mempunyai kolom identitas `nama`, `daerah`, dan 204 fitur hasil ekstraksi CO, NO₂, serta SO₂.

## 2. Dataset Linear dan Polynomial

Dua metode interpolasi digunakan untuk mengetahui pengaruh metode pengisian data terhadap hasil clustering.

### 2.1 Interpolasi Linear

Interpolasi linear memperkirakan nilai kosong dengan membentuk garis lurus antara nilai sebelum dan sesudah data yang kosong.

Secara umum, rumus interpolasi linear adalah:

$$
y =
y_1+
\frac{x-x_1}{x_2-x_1}
(y_2-y_1)
$$

Hasil interpolasi linear disimpan dalam:

- `Timeseries_CO_NO2_SO2_AsemRowo_Linear.csv`
- `All-Pollutants-AsemRowo-TSFEL-Linear.csv`

### 2.2 Interpolasi Polynomial

Interpolasi polynomial memperkirakan nilai kosong menggunakan kurva polynomial yang mengikuti pola beberapa titik data di sekitarnya.

Hasil interpolasi polynomial disimpan dalam:

- `Timeseries_CO_NO2_SO2_AsemRowo_Polynomial.csv`
- `All-Pollutants-AsemRowo-TSFEL-Polynomial.csv`

Masing-masing file hasil ekstraksi TSFEL mempunyai ukuran:

$$
1 \text{ baris} \times 204 \text{ kolom}
$$

Hasil pemeriksaan menunjukkan bahwa kedua file tidak mempunyai missing value maupun nilai infinity.

## 3. Preprocessing Data pada KNIME

Sebelum PCA dan clustering dilakukan, data melewati beberapa tahapan preprocessing.

### 3.1 Pemilihan Data

Data linear dan polynomial diambil dari tabel MySQL menggunakan **DB Query Reader**.

Kolom `nama` dan `daerah` tetap dipertahankan sebagai identitas setiap data. Kedua kolom tersebut tidak digunakan dalam perhitungan PCA dan K-Means.

### 3.2 Column Filter

Node **Column Filter** digunakan untuk memisahkan kolom numerik dari kolom identitas.

Kolom yang digunakan dalam proses perhitungan adalah kolom fitur numerik, sedangkan `nama` dan `daerah` dipertahankan agar hasil cluster dapat dikembalikan kepada pemilik data dan ditampilkan pada peta.

### 3.3 Normalizer

Node **Normalizer** digunakan untuk menyamakan skala seluruh fitur.

Normalisasi diperlukan karena masing-masing fitur TSFEL mempunyai rentang nilai yang berbeda. Tanpa normalisasi, fitur yang memiliki nilai sangat besar dapat mendominasi perhitungan jarak pada PCA dan K-Means.

## 4. Reduksi Dimensi Menggunakan PCA

Principal Component Analysis atau PCA digunakan untuk mengurangi jumlah dimensi data dengan membentuk komponen utama baru.

PCA mengubah fitur awal menjadi komponen yang tidak saling berkorelasi dengan tetap mempertahankan informasi penting dalam data.

Eksperimen dilakukan menggunakan tiga konfigurasi dimensi:

| Eksperimen | Jumlah Dimensi |
|---|---:|
| PCA 203 | 203 |
| PCA 74 | 74 |
| PCA 37 | 37 |

Ketiga konfigurasi PCA diterapkan pada dataset hasil interpolasi linear dan polynomial.

Tujuan eksperimen ini adalah membandingkan kualitas clustering ketika menggunakan jumlah dimensi yang berbeda.

## 5. Clustering Menggunakan K-Means

Data hasil PCA digunakan sebagai masukan pada algoritma **K-Means**.

K-Means mengelompokkan data berdasarkan kemiripan karakteristik. Setiap data dimasukkan ke cluster dengan pusat atau centroid terdekat.

Eksperimen jumlah cluster dilakukan menggunakan:

$$
k = 2,\ 3,\ 4,\ 5
$$

Setiap nilai `k` diuji pada:

- Data linear PCA 203.
- Data linear PCA 74.
- Data linear PCA 37.
- Data polynomial PCA 203.
- Data polynomial PCA 74.
- Data polynomial PCA 37.

Dengan demikian, jumlah eksperimen yang dilakukan adalah:

$$
2 \text{ metode}
\times
3 \text{ dimensi}
\times
4 \text{ nilai } k
=
24 \text{ eksperimen}
$$

## 6. Evaluasi Menggunakan Silhouette Coefficient

Silhouette Coefficient digunakan untuk mengevaluasi kualitas hasil clustering.

Untuk setiap data ke-$i$, nilai silhouette dihitung dengan rumus:

$$
s(i)=
\frac{b(i)-a(i)}
{\max\{a(i),b(i)\}}
$$

Keterangan:

- $a(i)$ adalah rata-rata jarak data ke-$i$ dengan anggota cluster yang sama.
- $b(i)$ adalah rata-rata jarak terkecil data ke-$i$ dengan cluster lain.
- $s(i)$ adalah nilai silhouette data ke-$i$.

Nilai silhouette berada dalam rentang:

$$
-1 \leq s(i) \leq 1
$$

Interpretasinya adalah:

- Nilai mendekati 1 menunjukkan data sudah berada pada cluster yang sesuai.
- Nilai mendekati 0 menunjukkan data berada di antara dua cluster.
- Nilai negatif menunjukkan data kemungkinan berada pada cluster yang kurang sesuai.

## 7. Hasil Eksperimen Dataset Polynomial

Hasil Silhouette Coefficient pada dataset polynomial adalah sebagai berikut:

| Dimensi PCA | k = 2 | k = 3 | k = 4 | k = 5 |
|---:|---:|---:|---:|---:|
| PCA 203 | 0.125 | 0.038 | 0.082 | 0.106 |
| PCA 74 | 0.125 | 0.038 | 0.082 | 0.106 |
| PCA 37 | 0.125 | 0.038 | 0.082 | 0.106 |

Nilai silhouette tertinggi pada dataset polynomial adalah:

$$
0.125
$$

Nilai tersebut diperoleh ketika menggunakan:

$$
k=2
$$

Dengan demikian, konfigurasi cluster terbaik pada dataset polynomial adalah **dua cluster**.

## 8. Hasil Eksperimen Dataset Linear

Hasil Silhouette Coefficient pada dataset linear adalah sebagai berikut:

| Dimensi PCA | k = 2 | k = 3 | k = 4 | k = 5 |
|---:|---:|---:|---:|---:|
| PCA 203 | 0.249 | **0.255** | 0.113 | 0.132 |
| PCA 74 | 0.249 | **0.255** | 0.113 | 0.132 |
| PCA 37 | 0.249 | **0.255** | 0.113 | 0.132 |

Nilai silhouette tertinggi pada dataset linear adalah:

$$
0.255
$$

Nilai tersebut diperoleh ketika menggunakan:

$$
k=3
$$

Dengan demikian, konfigurasi cluster terbaik pada dataset linear adalah **tiga cluster**.

## 9. Perbandingan Linear dan Polynomial

Ringkasan hasil terbaik kedua metode adalah:

| Metode Interpolasi | Dimensi yang Dipilih | Cluster Terbaik | Silhouette |
|---|---:|---:|---:|
| Linear | PCA 37 | 3 | **0.255** |
| Polynomial | PCA 37 | 2 | 0.125 |

Dataset linear menghasilkan nilai silhouette yang lebih tinggi daripada dataset polynomial.

Selisih nilai silhouette terbaik adalah:

$$
0.255-0.125=0.130
$$

Berdasarkan hasil tersebut, metode terbaik yang digunakan pada hasil akhir adalah:

- Metode interpolasi: **Linear**
- Reduksi dimensi: **PCA 37**
- Jumlah cluster: **3**
- Silhouette Coefficient: **0.255**

PCA 37 dipilih karena menghasilkan kualitas clustering yang sama dengan PCA 203 dan PCA 74, tetapi menggunakan jumlah dimensi yang lebih sedikit.

## 10. Workflow KNIME

Workflow KNIME terdiri atas beberapa node utama berikut:

1. **MySQL Connector** untuk membuat koneksi dengan database MySQL.
2. **DB Query Reader** untuk membaca tabel linear dan polynomial.
3. **Column Filter** untuk memilih kolom fitur dan memisahkan kolom identitas.
4. **Normalizer** untuk menyamakan skala fitur.
5. **PCA Compute** untuk membentuk model PCA.
6. **PCA Apply** untuk menghasilkan dimensi PCA 203, 74, dan 37.
7. **K-Means** untuk membentuk cluster dengan nilai `k` dari 2 sampai 5.
8. **Silhouette Coefficient** untuk mengevaluasi hasil clustering.
9. **Column Appender** atau node penggabungan untuk mengembalikan kolom `nama` dan `daerah`.
10. **CSV Writer** untuk menyimpan hasil clustering terbaik.

Hasil akhir KNIME disimpan dalam file:

`Hasil_Clustering_Linear_PCA37_K3.csv`

File tersebut mempunyai ukuran:

$$
37 \text{ baris} \times 40 \text{ kolom}
$$

Kolom pada file terdiri atas:

- `nama`
- `daerah`
- `PCA dimension 0` sampai `PCA dimension 36`
- `Cluster`

## 11. Hasil Clustering Terbaik

Hasil akhir membagi 37 data mahasiswa menjadi tiga kelompok:

- `cluster_0`
- `cluster_1`
- `cluster_2`

Data atas nama **Riska Nana Nuril Fadilah** dari **Asemrowo, Surabaya** termasuk dalam:

$$
\text{cluster\_1}
$$

Perlu diperhatikan bahwa nomor cluster hanya merupakan label kelompok. Label `cluster_0`, `cluster_1`, dan `cluster_2` tidak menunjukkan urutan kualitas dari yang paling baik sampai paling buruk.

## 12. Peta Interaktif Hasil Clustering

Hasil clustering ditampilkan pada peta berdasarkan kolom `daerah`.

Koordinat setiap daerah diperoleh melalui proses geocoding. Seluruh 37 daerah berhasil mendapatkan koordinat sehingga tidak terdapat data yang gagal ditampilkan.

File koordinat disimpan dalam:

`Hasil_Clustering_Linear_PCA37_K3_Koordinat.csv`

Peta interaktif disimpan dalam:

`Peta_Clustering_Linear_PCA37_K3.html`

Peta berikut menampilkan hasil clustering Linear PCA 37 dengan K-Means `k=3`.

<iframe
    src="_static/Peta_Clustering_Linear_PCA37_K3.html"
    width="100%"
    height="700"
    style="border: 1px solid #cccccc; border-radius: 8px;"
    loading="lazy">
</iframe>

Warna pada peta menunjukkan cluster yang berbeda:

- Merah menunjukkan `cluster_0`.
- Biru menunjukkan `cluster_1`.
- Hijau menunjukkan `cluster_2`.

Peta dapat digeser, diperbesar, dan diperkecil. Setiap titik dapat diklik untuk menampilkan nama mahasiswa, daerah, hasil cluster, metode interpolasi, jumlah dimensi PCA, dan nilai `k`.

## 13. Interpretasi Hasil

Hasil eksperimen menunjukkan bahwa metode interpolasi memberikan pengaruh terhadap kualitas clustering.

Dataset linear menghasilkan silhouette tertinggi sebesar `0.255`, sedangkan dataset polynomial hanya menghasilkan silhouette tertinggi sebesar `0.125`.

Nilai `0.255` menunjukkan bahwa struktur cluster sudah terbentuk, tetapi pemisahan antar-cluster masih tergolong lemah. Beberapa data masih mempunyai karakteristik yang hampir sama dengan data pada cluster lain.

Kesamaan nilai silhouette antara PCA 203, PCA 74, dan PCA 37 menunjukkan bahwa pengurangan dimensi sampai 37 tidak menurunkan kualitas clustering pada eksperimen ini.

Oleh karena itu, PCA 37 lebih efisien digunakan karena:

1. Menggunakan dimensi yang lebih sedikit.
2. Menghasilkan nilai silhouette yang sama dengan PCA 203 dan PCA 74.
3. Mempermudah penyimpanan dan pengolahan data.
4. Tetap menghasilkan tiga cluster sebagai hasil terbaik pada dataset linear.

## 14. Kesimpulan

Tiga polutan, yaitu CO, NO₂, dan SO₂, berhasil digabungkan menjadi 204 fitur TSFEL.

Missing value dan outlier ditangani menggunakan dua metode, yaitu interpolasi linear dan polynomial. Kedua hasil tersebut kemudian dianalisis menggunakan PCA dan K-Means pada KNIME.

Eksperimen dilakukan menggunakan PCA 203, PCA 74, dan PCA 37 dengan jumlah cluster dari `k=2` sampai `k=5`.

Hasil terbaik dataset polynomial diperoleh pada `k=2` dengan Silhouette Coefficient sebesar `0.125`.

Hasil terbaik secara keseluruhan diperoleh pada dataset linear dengan `k=3` dan Silhouette Coefficient sebesar `0.255`.

Karena PCA 203, PCA 74, dan PCA 37 menghasilkan nilai silhouette yang sama, PCA 37 dipilih sebagai hasil akhir karena menggunakan jumlah dimensi paling sedikit.

Konfigurasi akhir yang digunakan adalah:

| Komponen | Hasil Akhir |
|---|---|
| Metode interpolasi | Linear |
| Jumlah fitur awal | 204 fitur |
| Reduksi dimensi | PCA 37 |
| Jumlah cluster | 3 |
| Silhouette Coefficient | 0.255 |
| Jumlah data | 37 mahasiswa |
| Hasil Riska Nana Nuril Fadilah | `cluster_1` |
| Visualisasi | Peta interaktif |

Seluruh 37 hasil clustering berhasil ditampilkan pada peta interaktif berdasarkan daerah masing-masing.