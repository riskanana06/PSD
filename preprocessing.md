# Preprocessing Data

Preprocessing dilakukan untuk membersihkan data deret waktu CO, NO₂, dan SO₂ sebelum digunakan pada tahap ekstraksi fitur. Tahapan ini meliputi penyeragaman periode, pemeriksaan nilai negatif, deteksi outlier, dan imputasi missing value.

## 1. Penyeragaman Periode

Data dibatasi mulai **31 Agustus 2025 sampai 31 Agustus 2026**. Seluruh data kemudian disusun ulang menggunakan interval harian.

Periode tersebut menghasilkan:

\[
366 \text{ tanggal pengamatan}
\]

Struktur data setelah penyeragaman periode terdiri atas:

| Kolom | Keterangan |
|---|---|
| `date` | Tanggal pengamatan harian |
| `CO` | Nilai karbon monoksida |
| `NO2` | Nilai nitrogen dioksida |
| `SO2` | Nilai sulfur dioksida |

## 2. Pemeriksaan Missing Value

Missing value merupakan kondisi ketika nilai polutan pada tanggal tertentu tidak tersedia. Pemeriksaan awal menunjukkan bahwa setiap polutan masih memiliki missing value.

| Polutan | Jumlah data | Missing value awal |
|---|---:|---:|
| CO | 366 | 167 |
| NO₂ | 366 | 175 |
| SO₂ | 366 | 141 |

Missing value tersebut perlu ditangani agar data dapat digunakan dalam proses ekstraksi fitur dan analisis lanjutan.

## 3. Pemeriksaan Nilai Negatif

Konsentrasi polutan tidak seharusnya memiliki nilai negatif. Oleh karena itu, dilakukan pemeriksaan terhadap nilai yang lebih kecil dari nol.

Hasil pemeriksaan menunjukkan:

| Polutan | Nilai negatif |
|---|---:|
| CO | 0 |
| NO₂ | 0 |
| SO₂ | 93 |

Sebanyak **93 nilai negatif ditemukan pada SO₂**. Nilai tersebut dianggap sebagai data tidak valid, kemudian dikosongkan agar dapat diperbaiki melalui proses imputasi.

## 4. Deteksi Outlier Menggunakan IQR

Outlier merupakan nilai yang berada jauh dari sebagian besar data. Deteksi outlier dilakukan menggunakan metode **Interquartile Range (IQR)**.

Rumus IQR adalah:

\[
IQR = Q_3-Q_1
\]

Batas bawah dihitung menggunakan:

\[
\text{Lower Bound}=Q_1-1{,}5\times IQR
\]

Batas atas dihitung menggunakan:

\[
\text{Upper Bound}=Q_3+1{,}5\times IQR
\]

Keterangan:

- \(Q_1\) merupakan kuartil pertama atau persentil ke-25.
- \(Q_3\) merupakan kuartil ketiga atau persentil ke-75.
- \(IQR\) merupakan selisih antara \(Q_3\) dan \(Q_1\).
- Nilai yang lebih kecil dari batas bawah atau lebih besar dari batas atas dikategorikan sebagai outlier.

Hasil deteksi outlier adalah sebagai berikut:

| Polutan | Batas bawah | Batas atas | Jumlah outlier |
|---|---:|---:|---:|
| CO | 0.021211 | 0.038740 | 6 |
| NO₂ | 0.000003 | 0.000102 | 12 |
| SO₂ | -0.000302 | 0.000802 | 2 |

Nilai yang terdeteksi sebagai outlier dikosongkan terlebih dahulu agar tidak memengaruhi pola data.

## 5. Imputasi Missing Value

Setelah nilai negatif dan outlier ditandai sebagai data kosong, dilakukan imputasi menggunakan metode **interpolasi**.

Interpolasi memperkirakan nilai yang kosong berdasarkan nilai sebelum dan sesudahnya. Secara sederhana, interpolasi linear dapat dituliskan sebagai:

\[
y=y_1+\frac{x-x_1}{x_2-x_1}(y_2-y_1)
\]

Keterangan:

- \(y\) adalah nilai yang akan diperkirakan.
- \(y_1\) adalah nilai sebelum data kosong.
- \(y_2\) adalah nilai setelah data kosong.
- \(x_1\) dan \(x_2\) adalah posisi waktu dari kedua nilai tersebut.
- \(x\) adalah posisi waktu data yang kosong.

Metode ini dipilih karena data yang digunakan merupakan data deret waktu harian sehingga nilai yang berdekatan masih mempunyai hubungan berdasarkan waktu.

## 6. Hasil Akhir Preprocessing

Setelah seluruh tahap preprocessing selesai, diperoleh hasil berikut:

| Polutan | Jumlah data akhir | Missing value akhir | Nilai negatif akhir |
|---|---:|---:|---:|
| CO | 366 | 0 | 0 |
| NO₂ | 366 | 0 | 0 |
| SO₂ | 366 | 0 | 0 |

Dataset gabungan setelah preprocessing memiliki ukuran:

\[
366 \text{ baris}\times4 \text{ kolom}
\]

Empat kolom tersebut terdiri atas satu kolom tanggal dan tiga kolom polutan.

File hasil preprocessing disimpan dengan nama:

`Timeseries_CO_NO2_SO2_AsemRowo_Clean.csv`

## 7. Kesimpulan

Preprocessing berhasil dilakukan terhadap data CO, NO₂, dan SO₂ di Kecamatan Asem Rowo. Proses ini mencakup penyeragaman periode, pemeriksaan missing value, penanganan nilai negatif, deteksi outlier menggunakan IQR, dan imputasi menggunakan interpolasi.

Hasil akhir terdiri atas 366 data harian untuk setiap polutan dengan **0 missing value** dan **0 nilai negatif**. Dengan demikian, data sudah siap digunakan untuk ekstraksi fitur TSFEL dan analisis selanjutnya.