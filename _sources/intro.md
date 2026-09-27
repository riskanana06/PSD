# Proyek Sains Data

Selamat datang di dokumentasi proyek mata kuliah **Proyek Sains Data**. Proyek ini membahas pengolahan dan analisis data polutan udara di Kecamatan Asem Rowo, Kota Surabaya.

## Profil Mahasiswa

| Biodata | Keterangan |
|---|---|
| Nama Lengkap | Riska Nana Nuril Fadilah |
| NIM | 240411100081 |
| Program Studi | Teknik Informatika |
| Mata Kuliah | Proyek Sains Data |

## Judul Proyek

**Analisis Deret Waktu dan Clustering Data Polutan Udara CO, NO₂, dan SO₂ di Kecamatan Asem Rowo**

## Gambaran Proyek

Proyek ini menggunakan data tiga jenis polutan udara, yaitu:

- Karbon monoksida (CO).
- Nitrogen dioksida (NO₂).
- Sulfur dioksida (SO₂).

Data diperoleh dari pengamatan satelit Sentinel-5P melalui layanan openEO. Wilayah pengambilan data dibatasi menggunakan polygon GeoJSON agar penelitian berfokus pada Kecamatan Asem Rowo, Kota Surabaya.

Periode data yang digunakan adalah **31 Agustus 2025 sampai 31 Agustus 2026** dengan interval pengamatan harian. Dataset lengkap mempunyai 366 tanggal pengamatan.

## Tahapan Proyek

Tahapan yang dilakukan dalam proyek ini meliputi:

1. Menentukan wilayah pengamatan menggunakan GeoJSON.
2. Mengambil data CO, NO₂, dan SO₂ melalui openEO.
3. Menyimpan data deret waktu dalam format CSV.
4. Melakukan eksplorasi dan data understanding.
5. Mendeteksi missing value, nilai negatif, dan outlier.
6. Melakukan preprocessing dan interpolasi data.
7. Menyimpan data ke PostgreSQL Aiven.
8. Membaca dan menganalisis data menggunakan KNIME.
9. Mengekstraksi 68 fitur TSFEL dari setiap polutan.
10. Menggabungkan seluruh hasil ekstraksi menjadi 204 fitur.
11. Melakukan normalisasi dan reduksi dimensi menggunakan PCA.
12. Melakukan clustering menggunakan K-Means.
13. Mengevaluasi hasil clustering menggunakan Silhouette Coefficient.
14. Menampilkan hasil analisis melalui Jupyter Book dan GitHub Pages.

## Ringkasan Data

| Komponen | Keterangan |
|---|---|
| Wilayah | Kecamatan Asem Rowo, Kota Surabaya |
| Periode | 31 Agustus 2025–31 Agustus 2026 |
| Interval | Harian |
| Jumlah tanggal | 366 |
| Polutan | CO, NO₂, dan SO₂ |
| Sumber data | Sentinel-5P melalui openEO |
| Jumlah fitur setiap polutan | 68 |
| Jumlah fitur gabungan | 204 |
| Jumlah data windowed | 49 |
| Komponen PCA | 37 |
| Metode clustering | K-Means |
| Cluster terbaik | 2 cluster |

## Hasil Utama

Beberapa hasil utama yang diperoleh adalah:

- Data bersih mempunyai 366 baris tanpa missing value.
- Tidak terdapat nilai negatif pada data hasil preprocessing.
- CO, NO₂, dan SO₂ masing-masing berhasil diekstraksi menjadi 68 fitur.
- Seluruh fitur berhasil digabungkan menjadi 204 fitur.
- Ekstraksi menggunakan sistem window menghasilkan 49 sampel.
- Low Variance Filter menyisakan 174 fitur.
- PCA berhasil mengurangi data menjadi 37 komponen utama.
- Total explained variance dari 37 komponen PCA mencapai sekitar 98,93%.
- Jumlah cluster terbaik berdasarkan analisis data windowed adalah dua cluster.

## Isi Dokumentasi

Dokumentasi ini terdiri atas beberapa bagian:

- **Business Understanding** menjelaskan latar belakang, tujuan, manfaat, dan ruang lingkup penelitian.
- **Wilayah Pengamatan** menjelaskan lokasi, koordinat, dan penggunaan GeoJSON.
- **Data Understanding** menjelaskan karakteristik data CO, NO₂, dan SO₂.
- **Preprocessing** menjelaskan penanganan missing value, nilai negatif, dan outlier.
- **Time Series** menampilkan perubahan nilai polutan berdasarkan waktu.
- **PostgreSQL Aiven** menjelaskan penyimpanan data dan analisis Statistics menggunakan KNIME.
- **Ekstraksi Fitur TSFEL** menjelaskan ekstraksi fitur dan perhitungan manual fitur spectral.
- **Clustering** menjelaskan Low Variance Filter, normalisasi, PCA, K-Means, dan evaluasi cluster.

## Tujuan Dokumentasi

Website ini dibuat sebagai dokumentasi seluruh proses pengerjaan proyek, mulai dari pengambilan data hingga analisis clustering. Dokumentasi disusun agar setiap proses, data, hasil, dan metode yang digunakan dapat dipahami serta diperiksa kembali.