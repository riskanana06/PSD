# Data Understanding

Tahap ini memaparkan gambaran umum dataset polutan udara, cakupan wilayah pengamatan, serta proses eksplorasi awal sebelum dilakukan pemrosesan lebih lanjut.

---

| Komponen | Keterangan |
| :--- | :--- |
| **Wilayah** | Kecamatan Asem Rowo, Kota Surabaya, Jawa Timur |
| **Polutan** | $\text{NO}_2$ (nitrogen dioksida) |
| **Periode** | 31-08-2025 sampai 31-08-2026 |
| **Frekuensi analisis** | Harian |
| **Jumlah tanggal** | 366 |
| **Sumber** | Sentinel-5P melalui openEO |

---

## $\text{NO}_2$

$\text{NO}_2$ adalah nitrogen dioksida, salah satu polutan udara yang dapat berkaitan dengan aktivitas pembakaran, terutama emisi kendaraan dan sumber pembakaran lainnya. Dalam proyek ini yang dianalisis adalah deret waktu $\text{NO}_2$ untuk wilayah Asem Rowo.

---

## Eksplorasi

Data awal memiliki nilai yang hilang karena tidak semua tanggal memiliki nilai hasil agregasi. Deteksi *outlier* dilakukan menggunakan metode **IQR (Interquartile Range)**. Setelah proses deteksi, terdapat **12 outlier** yang ditangani sebelum imputasi.