# Ekstraksi Fitur dan Clustering

## 1. Pengambilan Data

Data yang digunakan merupakan hasil ekstraksi fitur dari tiga jenis polutan, yaitu CO, NO2, dan SO2. Setiap polutan memiliki 68 fitur hasil ekstraksi menggunakan TSFEL sehingga seluruhnya menghasilkan 204 fitur.

Data hasil ekstraksi disimpan di database MySQL pada tiga tabel berbeda. Ketiga tabel tersebut kemudian diambil dan digabungkan menggunakan node **MySQL Connector** dan **DB Query Reader** pada KNIME.

Data gabungan yang berhasil diperoleh terdiri atas 36 baris data mahasiswa dengan fitur dari ketiga polutan.

## 2. Preprocessing Data

Sebelum dilakukan clustering, data melewati beberapa tahap preprocessing berikut:

1. **Low Variance Filter** digunakan untuk menghapus fitur yang memiliki nilai konstan atau variansi sangat rendah.
2. **Column Filter** digunakan untuk memilih kolom yang diperlukan serta menyisakan satu kolom `nama` dan satu kolom `daerah`.
3. **Normalizer** digunakan untuk menyamakan skala setiap fitur agar fitur dengan nilai besar tidak mendominasi proses clustering.

## 3. Reduksi Dimensi Menggunakan PCA

Data hasil normalisasi memiliki jumlah fitur yang cukup banyak. Oleh karena itu, digunakan metode **Principal Component Analysis (PCA)** untuk mengurangi jumlah dimensi data.

Proses PCA menghasilkan 37 komponen utama dengan nilai **information preservation sebesar 100%**. Artinya, seluruh informasi pada data yang digunakan masih dapat dipertahankan dalam 37 komponen utama tersebut.

## 4. Clustering Menggunakan K-Means

Hasil PCA kemudian digunakan sebagai masukan pada metode **K-Means**. Jumlah cluster terbaik ditentukan dengan membandingkan nilai **Silhouette Coefficient** untuk beberapa nilai `k`.

Hasil pengujian jumlah cluster adalah sebagai berikut:

| Jumlah Cluster | Silhouette Coefficient |
|---:|---:|
| 2 | 0.637 |
| 3 | 0.102 |
| 4 | 0.036 |

Nilai Silhouette Coefficient tertinggi diperoleh pada **k = 2**, yaitu sebesar **0.637**. Oleh karena itu, jumlah cluster yang digunakan pada hasil akhir adalah dua cluster.

## 5. Workflow KNIME

Berikut merupakan workflow KNIME yang digunakan untuk melakukan pengambilan data, preprocessing, reduksi dimensi menggunakan PCA, clustering K-Means, dan evaluasi hasil clustering.

```{figure} _static/workflow_knime_pca.jpeg
---
width: 100%
name: workflow-knime-pca
---
Workflow preprocessing, PCA, K-Means, dan evaluasi clustering pada KNIME.
```

Workflow tersebut terdiri atas beberapa node berikut:

- **MySQL Connector** untuk menghubungkan KNIME dengan database MySQL.
- **DB Query Reader** untuk mengambil dan menggabungkan data hasil ekstraksi fitur CO, NO2, dan SO2.
- **Low Variance Filter** untuk menghapus fitur dengan variansi rendah.
- **Column Filter** untuk memilih kolom yang digunakan.
- **Normalizer** untuk menyamakan skala setiap fitur.
- **PCA Compute** untuk menghitung model PCA.
- **PCA Apply** untuk menghasilkan 37 komponen utama.
- **K-Means** untuk membagi data menjadi dua cluster.
- **Silhouette Coefficient** untuk mengevaluasi kualitas hasil clustering.
- **Scatter Plot** untuk menampilkan persebaran hasil cluster.

## 6. Hasil Silhouette Coefficient

Berikut merupakan hasil evaluasi clustering menggunakan Silhouette Coefficient untuk dua cluster.

```{figure} _static/silhouette_pca.jpeg
---
width: 100%
name: silhouette-pca
---
Hasil Silhouette Coefficient pada K-Means dengan dua cluster.
```

Hasil evaluasi menunjukkan nilai silhouette untuk masing-masing cluster sebesar **0.690** dan **-0.266**, sedangkan nilai silhouette keseluruhan adalah **0.637**.

Nilai keseluruhan sebesar **0.637** menunjukkan bahwa hasil clustering memiliki struktur pengelompokan yang cukup baik. Sebagian besar data sudah berada pada kelompok yang sesuai, walaupun masih terdapat beberapa data yang memiliki kemiripan dengan cluster lainnya.

## 7. Visualisasi Hasil Clustering

Hasil clustering membagi data menjadi dua kelompok, yaitu `cluster_0` dan `cluster_1`. Setiap titik pada grafik mewakili nama mahasiswa berdasarkan gabungan fitur hasil ekstraksi CO, NO2, dan SO2.

```{figure} _static/Scatter_Plot.png
---
width: 100%
name: scatter-cluster-pca
---
Visualisasi hasil clustering menggunakan PCA dan K-Means.
```

Berdasarkan visualisasi tersebut, sebagian besar data termasuk dalam `cluster_1`, sedangkan beberapa data lainnya termasuk dalam `cluster_0`. Data atas nama **Riska Nana Nuril Fadilah** termasuk dalam `cluster_0`.

## 8. Kesimpulan

Berdasarkan proses yang telah dilakukan, data hasil ekstraksi fitur CO, NO2, dan SO2 berhasil digabungkan dan diproses menggunakan KNIME. PCA berhasil mengurangi dimensi data menjadi 37 komponen utama dengan mempertahankan 100% informasi.

Hasil evaluasi menunjukkan bahwa jumlah cluster terbaik adalah **dua cluster** dengan nilai Silhouette Coefficient sebesar **0.637**. Dengan demikian, kombinasi PCA dan K-Means dapat digunakan untuk mengelompokkan data berdasarkan kemiripan karakteristik fitur polutan. 