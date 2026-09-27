# Business Understanding

## 1. Latar Belakang

Kualitas udara merupakan salah satu faktor lingkungan yang dapat memengaruhi kesehatan manusia dan kondisi ekosistem. Aktivitas transportasi, industri, pembakaran bahan bakar, pergudangan, dan kegiatan masyarakat dapat menghasilkan berbagai jenis polutan udara.

Kecamatan Asem Rowo merupakan salah satu wilayah di Kota Surabaya yang mempunyai aktivitas permukiman, transportasi, industri, dan pergudangan. Kondisi tersebut membuat pemantauan perubahan polutan udara di wilayah Asem Rowo penting untuk dilakukan.

Pada proyek ini, kualitas udara diamati menggunakan tiga parameter polutan, yaitu:

- Karbon monoksida (CO).
- Nitrogen dioksida (NO₂).
- Sulfur dioksida (SO₂).

Data diperoleh dari pengamatan satelit Sentinel-5P melalui layanan openEO. Polygon GeoJSON digunakan untuk membatasi area pengambilan data agar penelitian berfokus pada wilayah Kecamatan Asem Rowo.

Periode pengamatan dimulai pada **31 Agustus 2025 sampai 31 Agustus 2026**. Data disusun sebagai deret waktu harian dengan total 366 tanggal pengamatan.

## 2. Permasalahan

Data pengamatan satelit tidak selalu menghasilkan nilai pada setiap tanggal. Beberapa pengamatan dapat kosong karena keterbatasan cakupan satelit, kondisi atmosfer, kualitas hasil pengamatan, atau proses penyaringan data.

Hasil pengumpulan data mentah menunjukkan:

| Polutan | Jumlah Hari | Data Terisi | Data Kosong |
|---|---:|---:|---:|
| CO | 366 | 199 | 167 |
| NO₂ | 366 | 191 | 175 |
| SO₂ | 366 | 225 | 141 |

Selain missing value, data juga mengandung beberapa kondisi yang perlu ditangani:

- Data CO mempunyai enam outlier.
- Data NO₂ mempunyai 12 outlier.
- Data mentah SO₂ mempunyai empat outlier.
- Data SO₂ mempunyai 93 nilai negatif.
- Skala nilai ketiga polutan berbeda.
- Jumlah fitur hasil ekstraksi cukup besar sehingga diperlukan reduksi dimensi.

Data perlu dieksplorasi dan diproses terlebih dahulu sebelum digunakan untuk ekstraksi fitur dan analisis clustering.

## 3. Pertanyaan Analisis

Beberapa pertanyaan yang ingin dijawab melalui proyek ini adalah:

1. Bagaimana perubahan harian CO, NO₂, dan SO₂ di Kecamatan Asem Rowo?
2. Berapa jumlah missing value, nilai negatif, dan outlier pada setiap polutan?
3. Bagaimana cara menghasilkan dataset yang lengkap tanpa missing value?
4. Karakteristik apa saja yang dapat diperoleh dari ekstraksi fitur TSFEL?
5. Bagaimana menggabungkan fitur dari ketiga polutan menjadi satu dataset?
6. Berapa jumlah komponen PCA yang digunakan untuk mewakili data?
7. Berapa jumlah cluster terbaik berdasarkan hasil evaluasi K-Means?
8. Seberapa baik kualitas hasil clustering berdasarkan Silhouette Coefficient?

## 4. Tujuan

Proyek ini bertujuan untuk:

1. Mengumpulkan data harian CO, NO₂, dan SO₂ di Kecamatan Asem Rowo.
2. Membatasi wilayah pengambilan data menggunakan polygon GeoJSON.
3. Menyimpan hasil pengambilan data dalam format CSV.
4. Mengetahui pola perubahan harian ketiga polutan melalui visualisasi deret waktu.
5. Mengidentifikasi missing value, outlier, dan nilai yang tidak wajar.
6. Menghasilkan data bersih tanpa missing value dan nilai negatif.
7. Mengekstraksi 68 fitur TSFEL dari setiap polutan.
8. Menggabungkan hasil ekstraksi ketiga polutan menjadi 204 fitur.
9. Menyimpan data deret waktu dan hasil ekstraksi fitur ke basis data.
10. Menghubungkan basis data dengan KNIME.
11. Mengurangi dimensi data menggunakan PCA.
12. Menentukan jumlah cluster terbaik menggunakan K-Means dan Silhouette Coefficient.
13. Menampilkan hasil analisis melalui Jupyter Book dan GitHub Pages.

## 5. Manfaat

Hasil analisis ini diharapkan dapat memberikan manfaat sebagai berikut:

1. Memberikan gambaran perubahan CO, NO₂, dan SO₂ di Kecamatan Asem Rowo selama satu tahun.
2. Membantu mengidentifikasi periode ketika nilai polutan mengalami kenaikan atau penurunan.
3. Menjadi sumber informasi awal untuk memahami kondisi polutan udara di wilayah Asem Rowo.
4. Menunjukkan proses penanganan missing value, nilai negatif, dan outlier pada data satelit.
5. Memberikan representasi numerik data deret waktu melalui ekstraksi fitur TSFEL.
6. Mendukung pengelompokan data berdasarkan kemiripan karakteristik fitur polutan.
7. Mendukung proses pembelajaran mengenai openEO, GeoJSON, PostgreSQL, MySQL, KNIME, TSFEL, PCA, dan K-Means.
8. Menjadi dasar untuk pengembangan analisis kualitas udara yang lebih lanjut.

## 6. Ruang Lingkup

Ruang lingkup proyek ini meliputi:

| Komponen | Keterangan |
|---|---|
| Wilayah penelitian | Kecamatan Asem Rowo, Kota Surabaya |
| Provinsi | Jawa Timur |
| Periode penelitian | 31 Agustus 2025–31 Agustus 2026 |
| Interval data | Harian |
| Jumlah tanggal | 366 hari |
| Polutan | CO, NO₂, dan SO₂ |
| Sumber data | Sentinel-5P melalui layanan openEO |
| Batas wilayah | Polygon GeoJSON |
| Format penyimpanan awal | CSV |
| Basis data | PostgreSQL Aiven dan database yang digunakan pada KNIME |
| Ekstraksi fitur | TSFEL |
| Jumlah fitur setiap polutan | 68 fitur |
| Jumlah fitur gabungan | 204 fitur |
| Reduksi dimensi | PCA menjadi 37 komponen |
| Metode clustering | K-Means |
| Evaluasi clustering | Silhouette Coefficient |
| Publikasi hasil | Jupyter Book dan GitHub Pages |

## 7. Tahapan Analisis

Tahapan yang dilakukan pada proyek ini adalah:

1. Menentukan wilayah penelitian menggunakan GeoJSON.
2. Mengambil data CO, NO₂, dan SO₂ melalui openEO.
3. Menyusun data menjadi deret waktu harian.
4. Menyimpan data mentah dalam format CSV.
5. Melakukan eksplorasi dan data understanding.
6. Mendeteksi missing value, nilai negatif, dan outlier.
7. Melakukan imputasi menggunakan interpolasi.
8. Memastikan data hasil preprocessing tidak memiliki missing value.
9. Mengekstraksi 68 fitur TSFEL dari setiap polutan.
10. Menggabungkan hasil ekstraksi menjadi 204 fitur.
11. Menggunakan sistem window untuk menghasilkan beberapa sampel analisis.
12. Menyimpan data ke basis data.
13. Mengambil data melalui KNIME.
14. Melakukan penyaringan fitur dengan variansi rendah.
15. Melakukan normalisasi data.
16. Melakukan reduksi dimensi menggunakan PCA.
17. Melakukan clustering menggunakan K-Means.
18. Mengevaluasi hasil clustering.
19. Menampilkan hasil analisis pada website statis.

## 8. Batasan Analisis

Data yang digunakan merupakan hasil penginderaan jauh Sentinel-5P yang dirata-ratakan secara spasial dalam batas wilayah penelitian. Data tersebut menggambarkan pengamatan kolom atmosfer dan bukan hasil pengukuran langsung menggunakan stasiun pemantau kualitas udara di permukaan.

Oleh karena itu, nilai yang diperoleh tidak langsung diartikan sebagai tingkat paparan udara yang dihirup masyarakat. Analisis ini lebih tepat digunakan untuk mempelajari pola perubahan polutan dari waktu ke waktu.

Missing value yang diisi melalui interpolasi merupakan nilai estimasi berdasarkan data pada tanggal terdekat. Nilai hasil interpolasi harus dibedakan dari nilai pengamatan asli agar interpretasi hasil tetap transparan.

Hasil clustering menunjukkan kemiripan karakteristik data berdasarkan fitur yang digunakan. Cluster yang terbentuk tidak secara langsung menunjukkan kategori resmi kualitas udara seperti baik, sedang, atau berbahaya.

## 9. Kriteria Keberhasilan

Proyek dinyatakan berhasil apabila:

1. Data CO, NO₂, dan SO₂ berhasil diperoleh untuk periode yang ditentukan.
2. Seluruh tanggal dalam periode penelitian tersedia dalam dataset.
3. Data mentah berhasil disimpan dalam format CSV.
4. Missing value, outlier, dan nilai negatif berhasil diidentifikasi.
5. Grafik deret waktu ketiga polutan berhasil dibuat.
6. Data hasil preprocessing mempunyai 366 baris tanpa missing value dan nilai negatif.
7. Setiap polutan berhasil diekstraksi menjadi 68 fitur TSFEL.
8. Ketiga hasil ekstraksi berhasil digabungkan menjadi 204 fitur.
9. Data berhasil disimpan dan diakses melalui basis data.
10. Data berhasil diproses menggunakan KNIME.
11. PCA berhasil menghasilkan 37 komponen utama.
12. Jumlah cluster terbaik berhasil ditentukan menggunakan evaluasi clustering.
13. Seluruh hasil berhasil ditampilkan pada Jupyter Book dan GitHub Pages.

## 10. Hasil yang Diharapkan

Hasil akhir yang diharapkan dari proyek ini adalah:

- Dataset mentah CO, NO₂, dan SO₂.
- Dataset bersih berisi 366 data harian.
- Grafik deret waktu sebelum dan sesudah preprocessing.
- Hasil ekstraksi 68 fitur dari setiap polutan.
- Dataset gabungan berisi 204 fitur.
- Dataset hasil normalisasi dan PCA.
- Hasil K-Means clustering.
- Hasil evaluasi jumlah cluster.
- Workflow KNIME.
- Dokumentasi proyek dalam bentuk website statis.

## 11. Kesimpulan

Proyek ini berfokus pada pengolahan dan analisis data polutan CO, NO₂, dan SO₂ di Kecamatan Asem Rowo. Proses dimulai dari pengambilan data menggunakan openEO dan GeoJSON, dilanjutkan dengan preprocessing, ekstraksi fitur TSFEL, penyimpanan basis data, reduksi dimensi PCA, serta clustering menggunakan K-Means.

Hasil analisis diharapkan dapat memberikan gambaran perubahan karakteristik polutan selama periode 31 Agustus 2025 sampai 31 Agustus 2026 serta menunjukkan penerapan pengolahan data deret waktu secara lengkap.