# Data Understanding

## 1. Gambaran Dataset

Dataset yang digunakan berisi data time series harian tiga polutan udara di Kecamatan Asem Rowo, Kota Surabaya. Data diperoleh dari Sentinel-5P melalui layanan openEO dengan batas wilayah menggunakan GeoJSON Kecamatan Asem Rowo.

Periode data dimulai pada 31 Agustus 2025 sampai 31 Agustus 2026. Setelah seluruh tanggal disusun secara berurutan, dataset mempunyai 366 baris pengamatan.

Dataset terdiri atas empat kolom:

| Fitur  | Tipe Data | Deskripsi                          |
| ------ | --------- | ---------------------------------- |
| `date` | Datetime  | Tanggal pengamatan harian          |
| `CO`   | Numerik   | Nilai pengamatan karbon monoksida  |
| `NO2`  | Numerik   | Nilai pengamatan nitrogen dioksida |
| `SO2`  | Numerik   | Nilai pengamatan sulfur dioksida   |

Nilai polutan berasal dari pengamatan kolom atmosfer Sentinel-5P. Nilai tersebut tidak langsung dianggap sebagai konsentrasi udara pada permukaan atau tingkat paparan yang dihirup manusia.

## 2. Karbon Monoksida (CO)

Karbon monoksida atau CO merupakan gas yang tidak berwarna dan tidak berbau. CO terbentuk akibat proses pembakaran yang tidak sempurna.

Beberapa sumber CO antara lain:

* emisi kendaraan bermotor;
* pembakaran bahan bakar;
* aktivitas industri;
* pembakaran sampah;
* kebakaran lahan atau vegetasi.

Dalam konsentrasi tinggi, CO dapat mengganggu kemampuan darah dalam membawa oksigen. Pada penelitian ini, data CO digunakan untuk melihat pola perubahan nilai CO secara harian di wilayah Asem Rowo.

Hasil pemeriksaan data CO:

| Statistik            |    Nilai |
| -------------------- | -------: |
| Jumlah tanggal       |      366 |
| Data terisi          |      199 |
| Data kosong          |      167 |
| Rata-rata            | 0.030106 |
| Median               | 0.030043 |
| Standar deviasi      | 0.003769 |
| Minimum              | 0.019625 |
| Maksimum             | 0.042720 |
| Jumlah nilai negatif |        0 |
| Jumlah outlier IQR   |        6 |

Data CO memiliki 167 missing value. Berdasarkan metode Interquartile Range, ditemukan enam nilai outlier. Tidak ditemukan nilai CO negatif maupun nilai nol.

## 3. Nitrogen Dioksida (NO₂)

Nitrogen dioksida atau NO₂ merupakan gas reaktif yang umumnya dihasilkan oleh proses pembakaran pada suhu tinggi.

Beberapa sumber NO₂ antara lain:

* kendaraan bermotor;
* pembangkit listrik;
* pembakaran bahan bakar fosil;
* aktivitas industri;
* alat berat dan mesin pembakaran.

Paparan NO₂ dalam jumlah tinggi dapat mengganggu sistem pernapasan. NO₂ juga berperan dalam pembentukan polutan sekunder di atmosfer.

Hasil pemeriksaan data NO₂:

| Statistik            |      Nilai |
| -------------------- | ---------: |
| Jumlah tanggal       |        366 |
| Data terisi          |        191 |
| Data kosong          |        175 |
| Rata-rata            | 0.00005843 |
| Median               | 0.00005019 |
| Standar deviasi      | 0.00003835 |
| Minimum              | 0.00000511 |
| Maksimum             | 0.00033235 |
| Jumlah nilai negatif |          0 |
| Jumlah outlier IQR   |         12 |

NO₂ memiliki jumlah missing value paling banyak, yaitu 175 data. Berdasarkan metode IQR, ditemukan 12 nilai outlier. Tidak ditemukan nilai NO₂ negatif maupun nilai nol.

## 4. Sulfur Dioksida (SO₂)

Sulfur dioksida atau SO₂ merupakan gas yang terutama dihasilkan dari pembakaran bahan bakar yang mengandung sulfur.

Beberapa sumber SO₂ antara lain:

* aktivitas industri;
* pembakaran batu bara dan minyak;
* pembangkit listrik;
* proses peleburan logam;
* aktivitas vulkanik.

SO₂ dapat menyebabkan iritasi pada sistem pernapasan dan berperan dalam pembentukan hujan asam.

Hasil pemeriksaan data SO₂:

| Statistik            |       Nilai |
| -------------------- | ----------: |
| Jumlah tanggal       |         366 |
| Data terisi          |         225 |
| Data kosong          |         141 |
| Rata-rata            |  0.00007109 |
| Median               |  0.00006744 |
| Standar deviasi      |  0.00031341 |
| Minimum              | -0.00107618 |
| Maksimum             |  0.00147138 |
| Jumlah nilai negatif |          93 |
| Jumlah outlier IQR   |           4 |

SO₂ mempunyai 141 missing value dan empat outlier berdasarkan metode IQR. Selain itu, terdapat 93 nilai negatif.

Nilai negatif pada data produk satelit tidak berarti terdapat konsentrasi SO₂ fisik yang benar-benar negatif. Nilai tersebut dapat muncul akibat noise, ketidakpastian instrumen, koreksi latar belakang, keterbatasan sensitivitas, atau proses pengolahan data ketika sinyal polutan sangat rendah. Nilai negatif perlu didokumentasikan dan ditangani secara konsisten pada tahap preprocessing.

## 5. Kelengkapan Data

Ringkasan kelengkapan data setiap polutan adalah sebagai berikut:

| Polutan | Total Data | Terisi | Kosong | Persentase Terisi | Persentase Kosong |
| ------- | ---------: | -----: | -----: | ----------------: | ----------------: |
| CO      |        366 |    199 |    167 |            54.37% |            45.63% |
| NO₂     |        366 |    191 |    175 |            52.19% |            47.81% |
| SO₂     |        366 |    225 |    141 |            61.48% |            38.52% |

SO₂ mempunyai tingkat kelengkapan paling tinggi, sedangkan NO₂ mempunyai jumlah missing value paling banyak. Missing value dapat terjadi karena tidak semua tanggal menghasilkan pengamatan satelit yang valid pada wilayah penelitian.

## 6. Deteksi Outlier dengan Metode IQR

Outlier dideteksi menggunakan metode Interquartile Range. Rumus yang digunakan adalah:

$$
IQR = Q_3 - Q_1
$$

Batas bawah dihitung menggunakan:

$$
\text{Batas bawah} = Q_1 - 1.5(IQR)
$$

Batas atas dihitung menggunakan:

$$
\text{Batas atas} = Q_3 + 1.5(IQR)
$$

Nilai yang lebih kecil dari batas bawah atau lebih besar dari batas atas dianggap sebagai outlier.

Hasil deteksi awal:

| Polutan |          Q1 |         Q3 | Batas Bawah | Batas Atas | Outlier |
| ------- | ----------: | ---------: | ----------: | ---------: | ------: |
| CO      |  0.02778410 | 0.03216637 |  0.02121070 | 0.03873977 |       6 |
| NO₂     |  0.00003989 | 0.00006456 |  0.00000289 | 0.00010156 |      12 |
| SO₂     | -0.00011281 | 0.00025075 | -0.00065815 | 0.00079609 |       4 |

Outlier tidak langsung dianggap sebagai kesalahan. Nilai tersebut perlu diperiksa berdasarkan tanggal, pola time series, dan karakteristik pengamatan satelit sebelum ditangani.

## 7. Temuan Data Aneh

Beberapa kondisi data yang perlu diperhatikan adalah:

1. Dataset memiliki missing value dalam jumlah cukup besar pada ketiga polutan.
2. Data CO mempunyai enam outlier.
3. Data NO₂ mempunyai 12 outlier dan variasi nilai maksimum yang cukup jauh dari median.
4. Data SO₂ mempunyai empat outlier.
5. Terdapat 93 nilai SO₂ negatif.
6. Skala nilai CO jauh lebih besar dibandingkan NO₂ dan SO₂.
7. Ketiga polutan tidak boleh dibandingkan langsung hanya berdasarkan besar angkanya karena karakteristik dan skala pengukurannya berbeda.
8. Data perlu distandardisasi sebelum digunakan dalam PCA dan K-Means clustering.

## 8. Rencana Penanganan Data

Tahapan yang dilakukan setelah data understanding adalah:

1. Mempertahankan dataset mentah sebagai data referensi.
2. Mengubah nilai outlier menjadi missing value agar dapat diimputasi.
3. Menangani nilai SO₂ negatif secara konsisten dan mendokumentasikan metode yang digunakan.
4. Mengisi missing value menggunakan interpolasi berdasarkan waktu.
5. Menggunakan `ffill` dan `bfill` untuk menangani nilai kosong yang tersisa pada awal atau akhir periode.
6. Memastikan seluruh polutan mempunyai 366 data dan tidak memiliki missing value.
7. Menyimpan hasil preprocessing dalam CSV terpisah.
8. Melakukan ekstraksi fitur menggunakan TSFEL.
9. Melakukan standardisasi sebelum PCA dan clustering.

## 9. Kesimpulan Data Understanding

Dataset telah mencakup periode satu tahun penuh, tetapi belum siap langsung digunakan untuk analisis lanjutan. Masih terdapat missing value, outlier, serta nilai negatif pada SO₂.

CO mempunyai 167 missing value dan enam outlier. NO₂ mempunyai 175 missing value dan 12 outlier. SO₂ mempunyai 141 missing value, empat outlier, serta 93 nilai negatif.

Oleh karena itu, tahap preprocessing diperlukan agar dataset menjadi lengkap, konsisten, dan dapat digunakan untuk ekstraksi fitur, PCA, serta K-Means clustering.