# Data Understanding

## 1. Gambaran Dataset

Dataset yang digunakan berisi data deret waktu harian dari tiga polutan udara di Kecamatan Asem Rowo, Kota Surabaya. Data diperoleh dari pengamatan Sentinel-5P melalui layanan openEO dengan batas wilayah yang ditentukan menggunakan GeoJSON.

Periode pengamatan dimulai pada **31 Agustus 2025 sampai 31 Agustus 2026**. Setelah seluruh tanggal disusun secara berurutan, dataset mempunyai 366 baris pengamatan.

Dataset terdiri atas empat kolom:

| Fitur | Tipe Data | Deskripsi |
|---|---|---|
| `date` | Datetime | Tanggal pengamatan harian |
| `CO` | Numerik | Nilai pengamatan karbon monoksida |
| `NO2` | Numerik | Nilai pengamatan nitrogen dioksida |
| `SO2` | Numerik | Nilai pengamatan sulfur dioksida |

Nilai polutan merupakan hasil pengamatan kolom atmosfer Sentinel-5P. Oleh karena itu, nilai tersebut tidak langsung dianggap sebagai konsentrasi udara pada permukaan atau tingkat paparan yang dihirup oleh manusia.

## 2. Karbon Monoksida (CO)

Karbon monoksida atau CO merupakan gas yang tidak berwarna dan tidak berbau. CO terbentuk akibat proses pembakaran yang tidak sempurna.

Beberapa sumber CO antara lain:

- Emisi kendaraan bermotor.
- Pembakaran bahan bakar.
- Aktivitas industri.
- Pembakaran sampah.
- Kebakaran lahan atau vegetasi.

Dalam konsentrasi tinggi, CO dapat mengganggu kemampuan darah dalam membawa oksigen. Pada penelitian ini, data CO digunakan untuk melihat perubahan nilai CO secara harian di wilayah Asem Rowo.

Hasil pemeriksaan awal data CO adalah sebagai berikut:

| Statistik | Nilai |
|---|---:|
| Jumlah tanggal | 366 |
| Data terisi | 199 |
| Data kosong | 167 |
| Rata-rata | 0.030106 |
| Median | 0.030043 |
| Standar deviasi | 0.003769 |
| Minimum | 0.019625 |
| Maksimum | 0.042720 |
| Jumlah nilai negatif | 0 |
| Jumlah outlier IQR | 6 |

Data CO memiliki 167 missing value. Berdasarkan metode Interquartile Range, ditemukan enam nilai outlier. Tidak ditemukan nilai negatif pada data CO.

## 3. Nitrogen Dioksida (NO₂)

Nitrogen dioksida atau NO₂ merupakan gas reaktif yang umumnya dihasilkan oleh proses pembakaran pada suhu tinggi.

Beberapa sumber NO₂ antara lain:

- Kendaraan bermotor.
- Pembangkit listrik.
- Pembakaran bahan bakar fosil.
- Aktivitas industri.
- Alat berat dan mesin pembakaran.

Paparan NO₂ dalam jumlah tinggi dapat mengganggu sistem pernapasan. NO₂ juga berperan dalam pembentukan polutan sekunder di atmosfer.

Hasil pemeriksaan awal data NO₂ adalah sebagai berikut:

| Statistik | Nilai |
|---|---:|
| Jumlah tanggal | 366 |
| Data terisi | 191 |
| Data kosong | 175 |
| Rata-rata | 0.00005843 |
| Median | 0.00005019 |
| Standar deviasi | 0.00003835 |
| Minimum | 0.00000511 |
| Maksimum | 0.00033235 |
| Jumlah nilai negatif | 0 |
| Jumlah outlier IQR | 12 |

NO₂ memiliki jumlah missing value paling banyak, yaitu 175 data. Berdasarkan metode IQR, ditemukan 12 nilai outlier. Tidak ditemukan nilai negatif pada data NO₂.

## 4. Sulfur Dioksida (SO₂)

Sulfur dioksida atau SO₂ merupakan gas yang terutama dihasilkan dari pembakaran bahan bakar yang mengandung sulfur.

Beberapa sumber SO₂ antara lain:

- Aktivitas industri.
- Pembakaran batu bara dan minyak.
- Pembangkit listrik.
- Proses peleburan logam.
- Aktivitas vulkanik.

SO₂ dapat menyebabkan iritasi pada sistem pernapasan dan berperan dalam pembentukan hujan asam.

Hasil pemeriksaan awal data SO₂ adalah sebagai berikut:

| Statistik | Nilai |
|---|---:|
| Jumlah tanggal | 366 |
| Data terisi | 225 |
| Data kosong | 141 |
| Rata-rata | 0.00007109 |
| Median | 0.00006744 |
| Standar deviasi | 0.00031341 |
| Minimum | -0.00107618 |
| Maksimum | 0.00147138 |
| Jumlah nilai negatif | 93 |
| Jumlah outlier IQR pada data mentah | 4 |

Pada pemeriksaan awal data mentah, SO₂ mempunyai 141 missing value, empat outlier berdasarkan metode IQR, dan 93 nilai negatif.

Nilai negatif pada data produk satelit tidak berarti terdapat konsentrasi SO₂ fisik yang benar-benar negatif. Nilai tersebut dapat muncul akibat noise, ketidakpastian instrumen, koreksi latar belakang, keterbatasan sensitivitas, atau proses pengolahan data ketika sinyal polutan sangat rendah.

Pada tahap preprocessing, 93 nilai negatif tersebut ditandai sebagai data tidak valid dan diubah menjadi missing value. Setelah nilai negatif dikeluarkan dari perhitungan, deteksi IQR dilakukan kembali dan ditemukan dua outlier pada data SO₂ yang tersisa.

## 5. Kelengkapan Data

Ringkasan kelengkapan data setiap polutan adalah sebagai berikut:

| Polutan | Total Data | Terisi | Kosong | Persentase Terisi | Persentase Kosong |
|---|---:|---:|---:|---:|---:|
| CO | 366 | 199 | 167 | 54.37% | 45.63% |
| NO₂ | 366 | 191 | 175 | 52.19% | 47.81% |
| SO₂ | 366 | 225 | 141 | 61.48% | 38.52% |

SO₂ mempunyai persentase data terisi paling tinggi, sedangkan NO₂ mempunyai jumlah missing value paling banyak.

Missing value dapat terjadi karena tidak semua tanggal menghasilkan pengamatan satelit yang valid pada wilayah penelitian. Kondisi awan, kualitas pengamatan, cakupan satelit, dan proses penyaringan data dapat menyebabkan nilai pada tanggal tertentu tidak tersedia.

## 6. Deteksi Outlier dengan Metode IQR

Outlier dideteksi menggunakan metode **Interquartile Range (IQR)**. Metode ini menggunakan kuartil pertama dan kuartil ketiga untuk menentukan batas nilai yang dianggap normal.

Rumus IQR adalah:

\[
IQR=Q_3-Q_1
\]

Batas bawah dihitung menggunakan:

\[
\text{Batas bawah}=Q_1-1{,}5\times IQR
\]

Batas atas dihitung menggunakan:

\[
\text{Batas atas}=Q_3+1{,}5\times IQR
\]

Keterangan:

- \(Q_1\) merupakan kuartil pertama atau persentil ke-25.
- \(Q_3\) merupakan kuartil ketiga atau persentil ke-75.
- \(IQR\) merupakan selisih antara \(Q_3\) dan \(Q_1\).
- Nilai di bawah batas bawah atau di atas batas atas dianggap sebagai outlier.

Hasil deteksi awal pada data mentah adalah sebagai berikut:

| Polutan | Q1 | Q3 | Batas Bawah | Batas Atas | Outlier |
|---|---:|---:|---:|---:|---:|
| CO | 0.02778410 | 0.03216637 | 0.02121070 | 0.03873977 | 6 |
| NO₂ | 0.00003989 | 0.00006456 | 0.00000289 | 0.00010156 | 12 |
| SO₂ | -0.00011281 | 0.00025075 | -0.00065815 | 0.00079609 | 4 |

Tabel tersebut menunjukkan hasil pemeriksaan awal sebelum nilai negatif SO₂ ditangani. Setelah 93 nilai negatif SO₂ dikeluarkan pada tahap preprocessing, batas IQR dihitung kembali dan ditemukan dua outlier SO₂.

Outlier tidak selalu berarti kesalahan pengamatan. Namun, pada penelitian ini outlier ditangani agar tidak memberikan pengaruh terlalu besar terhadap proses interpolasi, ekstraksi fitur, PCA, dan clustering.

## 7. Temuan Data Aneh

Berdasarkan eksplorasi awal, ditemukan beberapa kondisi data yang perlu diperhatikan:

1. Ketiga polutan mempunyai missing value dalam jumlah yang cukup besar.
2. Data CO mempunyai 167 missing value dan enam outlier.
3. Data NO₂ mempunyai 175 missing value dan 12 outlier.
4. Data mentah SO₂ mempunyai 141 missing value dan empat outlier.
5. Terdapat 93 nilai negatif pada data SO₂.
6. Setelah nilai negatif SO₂ ditandai sebagai data tidak valid, ditemukan dua outlier pada data yang tersisa.
7. Skala nilai CO jauh lebih besar dibandingkan NO₂ dan SO₂.
8. Ketiga polutan tidak dapat dibandingkan secara langsung hanya berdasarkan besar nilainya karena mempunyai karakteristik dan skala pengukuran yang berbeda.
9. Data perlu dinormalisasi sebelum digunakan dalam PCA dan K-Means agar fitur dengan nilai besar tidak mendominasi proses analisis.

## 8. Rencana Penanganan Data

Tahapan yang dilakukan setelah proses data understanding adalah:

1. Mempertahankan dataset mentah sebagai data referensi.
2. Menyeragamkan periode data menjadi 366 tanggal harian.
3. Menandai nilai negatif SO₂ sebagai data tidak valid.
4. Mendeteksi outlier menggunakan metode IQR.
5. Mengubah nilai outlier menjadi missing value.
6. Mengisi missing value menggunakan interpolasi berdasarkan waktu.
7. Menggunakan metode pengisian tambahan untuk nilai kosong pada awal atau akhir periode apabila masih diperlukan.
8. Memastikan setiap polutan mempunyai 366 data.
9. Memastikan tidak terdapat missing value dan nilai negatif pada hasil akhir.
10. Menyimpan hasil preprocessing ke dalam file CSV.
11. Melakukan ekstraksi 68 fitur TSFEL pada setiap polutan.
12. Menggabungkan hasil ekstraksi CO, NO₂, dan SO₂ menjadi 204 fitur.
13. Melakukan normalisasi sebelum PCA dan K-Means clustering.

## 9. Perbandingan Data Sebelum dan Sesudah Preprocessing

Ringkasan kondisi data sebelum dan sesudah preprocessing adalah sebagai berikut:

| Polutan | Missing Awal | Nilai Negatif Awal | Outlier yang Ditangani | Missing Akhir | Nilai Negatif Akhir |
|---|---:|---:|---:|---:|---:|
| CO | 167 | 0 | 6 | 0 | 0 |
| NO₂ | 175 | 0 | 12 | 0 | 0 |
| SO₂ | 141 | 93 | 2 setelah nilai negatif ditangani | 0 | 0 |

Perbedaan jumlah outlier SO₂ antara pemeriksaan data mentah dan hasil preprocessing terjadi karena perhitungan IQR dilakukan kembali setelah nilai negatif dikeluarkan. Pada data mentah ditemukan empat outlier, sedangkan setelah penanganan nilai negatif ditemukan dua outlier yang kemudian diproses.

## 10. Kesimpulan Data Understanding

Dataset telah mencakup periode pengamatan selama satu tahun, yaitu 31 Agustus 2025 sampai 31 Agustus 2026, dengan total 366 tanggal pengamatan.

Pada data awal, CO mempunyai 167 missing value dan enam outlier. NO₂ mempunyai 175 missing value dan 12 outlier. SO₂ mempunyai 141 missing value, empat outlier pada pemeriksaan awal, serta 93 nilai negatif.

Berdasarkan hasil data understanding, dataset belum dapat langsung digunakan untuk analisis lanjutan. Oleh karena itu, preprocessing diperlukan untuk menangani missing value, nilai negatif, dan outlier.

Setelah preprocessing, seluruh polutan mempunyai 366 data harian tanpa missing value dan tanpa nilai negatif. Data tersebut kemudian dapat digunakan untuk ekstraksi fitur TSFEL, reduksi dimensi menggunakan PCA, dan clustering menggunakan K-Means.