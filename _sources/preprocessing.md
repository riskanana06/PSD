# Preprocessing

Tahapan persiapan dan pembersihan data sebelum analisis deret waktu:

### 1. Penyeragaman periode
Data dibatasi tepat pada tanggal **31-08-2025 sampai 31-08-2026** dan direindex menjadi 366 tanggal harian.

---

### 2. Deteksi outlier — IQR

Rumus batas ambang pencilan:

$$
\begin{aligned}
\text{Lower Bound} &= Q_1 - 1,5 \times \text{IQR} \\
\text{Upper Bound} &= Q_3 + 1,5 \times \text{IQR} \\
\text{IQR} &= Q_3 - Q_1
\end{aligned}
$$

Dari data yang digunakan, diperoleh **12 nilai** yang ditandai sebagai *outlier*.

---

### 3. Imputasi missing value
Nilai *outlier* dikosongkan terlebih dahulu, kemudian nilai yang kosong diisi menggunakan **interpolasi berbasis waktu**. Hasil akhir memiliki **0 missing value**.

---

### Ringkasan Hasil Preprocessing

| 366 | 12 | 0 |
| :---: | :---: | :---: |
| **Jumlah data akhir** | **Outlier ditangani** | **Missing value akhir** |