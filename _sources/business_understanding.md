# Business Understanding

## 1. Latar Belakang

Kualitas udara merupakan salah satu faktor lingkungan yang dapat memengaruhi kesehatan manusia dan kondisi ekosistem. Aktivitas transportasi, industri, pembakaran bahan bakar, pergudangan, dan kegiatan masyarakat dapat menghasilkan berbagai polutan udara.

Kecamatan Asem Rowo merupakan salah satu wilayah di Kota Surabaya yang memiliki aktivitas permukiman, transportasi, industri, dan pergudangan. Kondisi tersebut membuat pemantauan perubahan polutan udara di wilayah Asem Rowo penting untuk dilakukan.

Pada proyek ini, kualitas udara diamati menggunakan tiga parameter polutan, yaitu karbon monoksida (CO), nitrogen dioksida (NO₂), dan sulfur dioksida (SO₂). Data diperoleh dari pengamatan satelit Sentinel-5P melalui layanan openEO. GeoJSON Kecamatan Asem Rowo digunakan untuk membatasi wilayah pengambilan data.

Periode pengamatan dimulai pada 31 Agustus 2025 sampai 31 Agustus 2026. Data disusun sebagai time series harian dengan total 366 tanggal pengamatan.

## 2. Permasalahan

Data pengamatan satelit tidak selalu menghasilkan nilai pada setiap tanggal. Beberapa pengamatan dapat kosong karena keterbatasan cakupan satelit, kondisi atmosfer, kualitas hasil pengamatan, atau proses penyaringan data.

Hasil pengumpulan data mentah menunjukkan:

| Polutan | Jumlah Hari | Data Terisi | Data Kosong |
| ------- | ----------: | ----------: | ----------: |
| CO      |         366 |         199 |         167 |
| NO₂     |         366 |         191 |         175 |
| SO₂     |         366 |         225 |         141 |

Selain missing value, data juga dapat mengandung nilai ekstrem atau outlier. Pada data CO ditemukan enam nilai yang berada di luar batas metode Interquartile Range (IQR). Data SO₂ juga memiliki beberapa nilai negatif yang perlu diperiksa karena dapat berkaitan dengan noise, ketidakpastian pengukuran, atau proses pengolahan data satelit.

Oleh karena itu, data perlu dieksplorasi dan diproses terlebih dahulu sebelum digunakan untuk ekstraksi fitur dan analisis lanjutan.

## 3. Tujuan

Proyek ini bertujuan untuk:

1. Mengumpulkan data harian CO, NO₂, dan SO₂ di Kecamatan Asem Rowo.
2. Membatasi wilayah pengambilan data menggunakan GeoJSON Kecamatan Asem Rowo.
3. Menyimpan hasil pengambilan data dalam format CSV.
4. Mengetahui pola perubahan harian ketiga polutan melalui visualisasi time series.
5. Mengidentifikasi missing value, outlier, dan nilai yang tidak wajar.
6. Menyiapkan data yang bersih untuk proses ekstraksi fitur menggunakan TSFEL.
7. Menyediakan dasar data untuk analisis PCA dan K-Means clustering pada tahap berikutnya.

## 4. Manfaat

Hasil analisis ini diharapkan dapat memberikan manfaat sebagai berikut:

1. Memberikan gambaran perubahan nilai CO, NO₂, dan SO₂ di Kecamatan Asem Rowo selama satu tahun.
2. Membantu mengidentifikasi periode ketika nilai polutan mengalami kenaikan atau penurunan.
3. Menjadi sumber informasi awal untuk memahami kondisi polutan udara di wilayah Asem Rowo.
4. Mendukung proses pembelajaran mengenai pengolahan data time series, deteksi outlier, imputasi missing value, ekstraksi fitur, reduksi dimensi, dan clustering.
5. Menjadi dasar untuk pengembangan analisis kualitas udara yang lebih lanjut.
6. Membantu pihak terkait dalam melakukan pemantauan lingkungan berbasis data penginderaan jauh.

## 5. Ruang Lingkup

Ruang lingkup proyek ini meliputi:

* Wilayah penelitian: Kecamatan Asem Rowo, Kota Surabaya, Jawa Timur.
* Periode penelitian: 31 Agustus 2025 sampai 31 Agustus 2026.
* Interval data: harian.
* Jumlah tanggal: 366 hari.
* Polutan yang dianalisis: CO, NO₂, dan SO₂.
* Sumber data: Sentinel-5P melalui layanan openEO Copernicus Data Space.
* Batas wilayah: GeoJSON Kecamatan Asem Rowo.
* Format penyimpanan: CSV.
* Analisis awal: eksplorasi data dan visualisasi time series.
* Analisis lanjutan: preprocessing, ekstraksi fitur TSFEL, PCA, dan K-Means clustering.

## 6. Batasan Analisis

Data yang digunakan merupakan hasil penginderaan jauh Sentinel-5P yang dirata-ratakan secara spasial dalam batas wilayah Kecamatan Asem Rowo. Data tersebut menggambarkan pengamatan kolom atmosfer dan bukan hasil pengukuran langsung menggunakan stasiun pemantau kualitas udara di permukaan.

Oleh karena itu, nilai yang diperoleh tidak langsung diartikan sebagai tingkat paparan udara yang dihirup masyarakat. Analisis ini lebih tepat digunakan untuk mempelajari pola perubahan polutan dari waktu ke waktu.

Missing value yang diisi melalui interpolasi merupakan nilai estimasi berdasarkan data pada tanggal terdekat. Nilai hasil interpolasi harus dibedakan dari nilai pengamatan asli agar interpretasi hasil tetap transparan.

## 7. Kriteria Keberhasilan

Proyek dinyatakan berhasil apabila:

1. Data CO, NO₂, dan SO₂ berhasil diperoleh untuk periode yang ditentukan.
2. Seluruh tanggal dalam periode penelitian tersedia dalam dataset.
3. Data mentah tersimpan dalam format CSV.
4. Missing value dan outlier dapat diidentifikasi serta didokumentasikan.
5. Grafik time series ketiga polutan berhasil dibuat.
6. Data hasil preprocessing tidak memiliki missing value.
7. Data dapat digunakan untuk ekstraksi fitur dan analisis lanjutan.
