# Proyek PCD: Klasifikasi Citra Susunan Sepatu Rapi dan Berantakan

Dokumentasi komprehensif proyek **Pengolahan Citra Digital (PCD)** untuk melakukan klasifikasi otomatis terhadap susunan sepatu ke dalam dua kategori: **Rapi** (*tidy*) dan **Berantakan** (*messy*), menggunakan kombinasi fitur statistik warna RGB, fitur tekstur matriks kookurensi spasial GLCM (*Gray-Level Co-occurrence Matrix*), dan pengklasifikasi *ensemble* Random Forest.

---

## 1. Business Understanding

### 1.1 Latar Belakang
Penataan alas kaki yang tertib dan teratur merupakan aspek penting dalam pengelolaan ruang hunian pribadi, perkantoran, tempat ibadah, asrama, dan fasilitas publik. Penataan manual mengandalkan persepsi manusia yang bersifat subjektif, memerlukan kehadiran fisik terus-menerus, dan tidak terotomatisasi.

Dengan memanfaatkan teknik pengolahan citra digital dan pembelajaran mesin, penilaian keteraturan susunan sepatu dapat dilakukan secara otomatis, objektif, dan terstandarisasi berdasarkan analisis kuantitatif pola warna dan tekstur visual.

### 1.2 Masalah Bisnis dan Komputasi
- **Heterogenitas Bentuk dan Warna:** Sepatu memiliki variasi model, warna, ukuran, dan bahan yang sangat beragam.
- **Kondisi Pengambilan Citra Alami:** Variasi pencahayaan ruangan dan sudut pandang kamera (*viewing angles*) yang tidak seragam.
- **Pencegahan Data Leakage:** Adanya foto *burst* dan duplikasi berkas mengharuskan pemisahan data yang ketat berbasis kelompok independen.

### 1.3 Tujuan Proyek
- Mengekstraksi 9 fitur statistik warna RGB dan 5 fitur tekstur spasial GLCM.
- Membangun dataset terpadu berdimensi 200 baris dengan 14 fitur prediktor numerik dan 1 label target.
- Mencegah kebocoran data (*zero data leakage*) menggunakan *Disjoint-Set Union* dan `StratifiedGroupKFold`.
- Melatih model Random Forest ($100\text{ trees}$, `random_state = 14`) dan mengevaluasi kinerjanya.

---

## 2. Data Understanding

- **Objek Citra:** Fokus murni pada susunan sepatu di lantai/rak.
- **Jumlah Data:** 200 citra (100 `rapi` dan 100 `berantakan`, seimbang 50:50).
- **Format File:** JPG, JPEG, dan HEIC.
  - Kategori Rapi: 71 JPG, 26 JPEG, 3 HEIC.
  - Kategori Berantakan: 63 JPG, 34 JPEG, 3 HEIC.
- **Audit Duplikasi dan Kemiripan Citra:**
  - **MD5 Checksum (Identik Biner):** 9 kelompok salinan file identik (5 kelompok rapi, 4 kelompok berantakan).
  - **dHash 64-bit (Kemiripan Perseptual):** 19 pasangan identik visual (jarak Hamming = 0) dan 6 pasangan *burst/near-duplicate* (jarak Hamming 1â€“5).
  - **Kelompok Independen:** 177 kelompok unik via *Disjoint-Set Union*.

---

## 3. Data Preparation

1. **Standardisasi Citra ke RGB:** Membaca citra berbagai format (termasuk dekode HEIF via `pillow-heif`) dan mengonversi ke mode RGB 3-channel bertipe `uint8` dengan rentang piksel $[0, 255]$.
2. **Isolasi Kelompok Duplikasi (Zero Data Leakage):**
   Menggunakan `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=14)`:
   - **Data Training:** 162 citra (81,0%) â€” 83 rapi, 79 berantakan.
   - **Data Testing:** 38 citra (19,0%) â€” 17 rapi, 21 berantakan.
   - **Overlapping Group:** 0 grup (100% bebas kebocoran data).

---

## 4. Ekstraksi Fitur Citra RGB

Pada setiap kanal warna $c \in \{R, G, B\}$, dihitung tiga besaran statistik:
- **Mean (Rata-rata Intensitas):**
  $$\mu_c = \frac{1}{M \cdot N} \sum_{i=1}^M \sum_{j=1}^N I_c(i, j)$$
- **Standard Deviation (Standar Deviasi):**
  $$\sigma_c = \sqrt{\frac{1}{M \cdot N} \sum_{i=1}^M \sum_{j=1}^N (I_c(i, j) - \mu_c)^2}$$
- **Skewness (Kemencengan Distribusi):**
  $$\gamma_c = \frac{\frac{1}{M \cdot N} \sum_{i=1}^M \sum_{j=1}^N (I_c(i, j) - \mu_c)^3}{\sigma_c^3}$$

Fitur yang dihasilkan: `mean_R`, `mean_G`, `mean_B`, `std_R`, `std_G`, `std_B`, `skew_R`, `skew_G`, `skew_B`. Disimpan pada `output/fitur_rgb_sementara.csv`.

---

## 5. Konversi Citra ke Grayscale

Citra dikonversi ke skala abu-abu 8-bit untuk mereduksi kompleksitas komputasi matriks GLCM. Menggunakan formula pembobotan luminansi perseptual ITU-R BT.601-2:

$$Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$

- Format: Array 2D single-channel, tipe data `uint8`, rentang $[0, 255]$.
- Sebanyak 200 citra disimpan di `output/grayscale/rapi/` dan `output/grayscale/berantakan/`.

---

## 6. Ekstraksi Fitur Tekstur Menggunakan GLCM

*Gray-Level Co-occurrence Matrix* (GLCM) menganalisis distribusi spasial pasangan piksel dengan parameter:
- Jarak piksel: $d = 1$
- Orientasi sudut: 4 arah ($\theta \in \{0^\circ, 45^\circ, 90^\circ, 135^\circ\}$)
- Level: $256$ aras keabuan
- Simetris: `True`, Normalisasi: `True` ($p(i, j)$)
- **Agregasi Invarian Rotasi:** Nilai akhir diperoleh dari rata-rata keempat sudut.

Lima fitur GLCM:
1. **Energy:** $\text{Energy} = \sqrt{\sum_{i}\sum_{j} p(i, j)^2}$
2. **Entropy:** $\text{Entropy} = -\sum_{i}\sum_{j} p(i, j) \log_2 p(i, j) \quad (\text{untuk } p(i, j) > 0)$
3. **Contrast:** $\text{Contrast} = \sum_{i}\sum_{j} |i - j|^2 p(i, j)$
4. **Correlation:** $\text{Correlation} = \sum_{i}\sum_{j} \frac{(i - \mu_i)(j - \mu_j) p(i, j)}{\sigma_i \sigma_j}$
5. **Homogeneity:** $\text{Homogeneity} = \sum_{i}\sum_{j} \frac{p(i, j)}{1 + |i - j|}$

Disimpan pada `output/fitur_glcm_sementara.csv`.

---

## 7. Penjelasan Lengkap 14 Fitur dan Formula

| No | Fitur | Kategori | Rentang Nilai | Formula KaTeX | Makna Fisis / Visual |
|:--:|---|---|:--:|---|---|
| 1 | `mean_R` | Warna (RGB) | $[0, 255]$ | $\mu_R = \frac{1}{MN} \sum I_R$ | Kecerahan rata-rata kanal merah |
| 2 | `mean_G` | Warna (RGB) | $[0, 255]$ | $\mu_G = \frac{1}{MN} \sum I_G$ | Kecerahan rata-rata kanal hijau |
| 3 | `mean_B` | Warna (RGB) | $[0, 255]$ | $\mu_B = \frac{1}{MN} \sum I_B$ | Kecerahan rata-rata kanal biru |
| 4 | `std_R` | Warna (RGB) | $[0, 127.5]$ | $\sigma_R = \sqrt{\frac{1}{MN} \sum (I_R - \mu_R)^2}$ | Kontras/variasi spektrum merah |
| 5 | `std_G` | Warna (RGB) | $[0, 127.5]$ | $\sigma_G = \sqrt{\frac{1}{MN} \sum (I_G - \mu_G)^2}$ | Kontras/variasi spektrum hijau |
| 6 | `std_B` | Warna (RGB) | $[0, 127.5]$ | $\sigma_B = \sqrt{\frac{1}{MN} \sum (I_B - \mu_B)^2}$ | Kontras/variasi spektrum biru |
| 7 | `skew_R` | Warna (RGB) | $[-\infty, +\infty]$ | $\gamma_R = \frac{\frac{1}{MN}\sum(I_R-\mu_R)^3}{\sigma_R^3}$ | Asimetri distribusi warna merah |
| 8 | `skew_G` | Warna (RGB) | $[-\infty, +\infty]$ | $\gamma_G = \frac{\frac{1}{MN}\sum(I_G-\mu_G)^3}{\sigma_G^3}$ | Asimetri distribusi warna hijau |
| 9 | `skew_B` | Warna (RGB) | $[-\infty, +\infty]$ | $\gamma_B = \frac{\frac{1}{MN}\sum(I_B-\mu_B)^3}{\sigma_B^3}$ | Asimetri distribusi warna biru |
| 10 | `energy` | Tekstur (GLCM) | $[0, 1]$ | $\sqrt{\sum p(i,j)^2}$ | Keseragaman pola tekstur |
| 11 | `entropy` | Tekstur (GLCM) | $[0, 8]$ | $-\sum p(i,j)\log_2 p(i,j)$ | Kompleksitas/keacakan tekstur |
| 12 | `contrast` | Tekstur (GLCM) | $[0, 65025]$ | $\sum |i-j|^2 p(i,j)$ | Variasi intensitas lokal |
| 13 | `correlation`| Tekstur (GLCM) | $[-1, 1]$ | $\sum \frac{(i-\mu_i)(j-\mu_j)p(i,j)}{\sigma_i \sigma_j}$ | Ketergantungan linier spasial |
| 14 | `homogeneity`| Tekstur (GLCM) | $[0, 1]$ | $\sum \frac{p(i,j)}{1 + |i-j|}$ | Kedekatan elemen ke diagonal |

Dataset final digabungkan menjadi satu berkas: `output/dataset_fitur_citra.csv` ($200 \times 15$).

---

## 8. Exploratory Data Analysis (EDA)

### 8.1 Statistik Deskriptif ($N = 200$)
- `mean_R`: mean 137,12, std 18,84, rentang [73,97 - 176,57]
- `mean_G`: mean 127,14, std 17,42, rentang [65,10 - 168,23]
- `mean_B`: mean 119,13, std 18,00, rentang [64,38 - 164,54]
- `std_R`: mean 59,76, std 10,39, rentang [36,28 - 89,31]
- `std_G`: mean 61,37, std 7,66, rentang [34,47 - 85,16]
- `std_B`: mean 62,20, std 7,40, rentang [32,04 - 80,29]
- `skew_R`: mean -0,30, std 0,46, rentang [-1,50 - 0,88]
- `skew_G`: mean -0,11, std 0,40, rentang [-1,26 - 0,86]
- `skew_B`: mean -0,05, std 0,40, rentang [-1,12 - 0,88]
- `energy`: mean 0,0327, std 0,0221, rentang [0,0138 - 0,2049]
- `entropy`: mean 11,6373, std 0,7721, rentang [8,6353 - 13,3113]
- `contrast`: mean 103,73, std 65,52, rentang [11,75 - 358,43]
- `correlation`: mean 0,9852, std 0,0090, rentang [0,9608 - 0,9988]
- `homogeneity`: mean 0,3915, std 0,1181, rentang [0,1676 - 0,7537]

### 8.2 Temuan Korelasi Antarfitur
- Korelasi linier individual terhadap label bersifat moderat/rendah ($|r| \le 0,16$). Hal ini menunjukkan perlunya model non-linear yang dapat mengeksploitasi interaksi fitur multidimensi.
- Terlihat hubungan invers yang kuat antara `contrast` dan `homogeneity` ($r \approx -0,80$), serta multikolinieritas alami antar-mean kanal warna ($r > 0,90$).

---

## 9. Implementasi dan Alur Klasifikasi Random Forest

- **Algoritma:** `RandomForestClassifier(n_estimators=100, random_state=14, criterion='gini')`
- **Penskalaan Fitur:** Tidak menggunakan scaler (Random Forest invarian terhadap skala fitur).
- **Integritas:** Model dilatih pada 162 sampel data latih dan diuji pada 38 sampel data uji independen.

---

## 10. Hasil Pengujian dan Evaluasi Model

### Kinerja pada Data Testing ($N = 38$):
- **Akurasi:** **71,05%** (27 dari 38 sampel diprediksi benar)
- **Macro Precision:** **72,12%**
- **Macro Recall:** **69,33%**
- **Macro F1-Score:** **69,33%**
- **Weighted Average F1-Score:** **70,10%**

### Detail Kinerja per Kelas:
- **Kategori Rapi:** Precision = 75,00%, Recall = 52,94%, F1-Score = 62,07% (Support = 17)
- **Kategori Berantakan:** Precision = 69,23%, Recall = 85,71%, F1-Score = 76,60% (Support = 21)

---

## 11. Confusion Matrix dan Pembahasannya

Matriks kontingensi ($2 \times 2$):

| Kelas Aktual \ Prediksi | Prediksi: Rapi | Prediksi: Berantakan | Total Aktual |
|---|:---:|:---:|:---:|
| **Aktual: Rapi** | **$TP = 9$** | **$FN = 8$** | 17 |
| **Aktual: Berantakan** | **$FP = 3$** | **$TN = 18$** | 21 |
| **Total Prediksi** | 12 | 26 | 38 |

- **Recall Berantakan sangat tinggi ($85,71\%$):** 18 dari 21 citra berantakan terdeteksi secara akurat berkat fitur kontras spasial dan dispersi warna.
- **Presisi Rapi mencapai $75,00\%$:** 9 dari 12 citra yang diprediksi rapi terbukti benar.
- **False Negative ($FN = 8$):** Dipicu oleh variasi warna alas sepatu yang mencolok serta sudut pengambilan foto yang miring (*perspective distortion*).

---

## 12. Feature Importance dan Interpretasinya

Kontribusi 14 fitur berdasarkan penurunan ketidakmurnian Gini:
1. `skew_G` : **9,12%** (0,0912) â€” Asimetri kanal hijau terhadap bayangan
2. `std_R` : **9,08%** (0,0908) â€” Variasi warna merah bodi sepatu
3. `correlation` : **8,69%** (0,0869) â€” Keteraturan linier pasangan piksel GLCM
4. `skew_B` : **8,60%** (0,0860) â€” Asimetri kanal biru
5. `contrast` : **7,82%** (0,0782) â€” Variasi kontras transisi lokal
6. `mean_B` : 7,22% (0,0722)
7. `mean_R` : 7,06% (0,0706)
8. `entropy` : 6,74% (0,0674)
9. `homogeneity` : 6,49% (0,0649)
10. `std_B` : 6,30% (0,0630)
11. `mean_G` : 6,22% (0,0622)
12. `skew_R` : 6,02% (0,0602)
13. `energy` : 5,53% (0,0553)
14. `std_G` : 5,11% (0,0511)

**Sinergi:** Kontribusi merata antara fitur warna (terutama skewness dan standar deviasi) serta fitur tekstur (korelasi dan kontras) membuktikan kedua modalitas saling melengkapi dalam klasifikasi susunan sepatu.

---

## 13. Analisis Hasil, Keterbatasan, dan Kesimpulan

1. **Akurasi:** Akurasi pengujian mencapai **71,05%** dengan validitas metodologis tinggi (*zero data leakage*).
2. **Keterbatasan:** Ukuran dataset 200 sampel (177 kelompok independen) dan ketiadaan pra-pemrosesan segmentasi latar belakang lantai.
3. **Pengembangan Lanjut:** Penerapan deteksi objek (YOLO) untuk memotong latar belakang serta transformasi garis Hough untuk mendeteksi sumbu kelurusan sepatu.

---

## 14. Struktur Direktori dan Panduan Eksekusi

```text
klasifikasi_citra_sepatu/
â”œâ”€â”€ README.md                           # Dokumentasi teknis proyek (berkas ini)
â”œâ”€â”€ .mplconfig/                         # Cache matplotlib
â”œâ”€â”€ notebooks/
â”‚   â””â”€â”€ klasifikasi_citra_sepatu.ipynb  # Jupyter Notebook klasifikasi interaktif
â”œâ”€â”€ output/
â”‚   â”œâ”€â”€ dataset_fitur_citra.csv         # Dataset final (200 baris Ã— 15 kolom)
â”‚   â”œâ”€â”€ fitur_rgb_sementara.csv         # Hasil 9 fitur warna RGB
â”‚   â”œâ”€â”€ fitur_glcm_sementara.csv        # Hasil 5 fitur tekstur GLCM
â”‚   â”œâ”€â”€ model_random_forest.pkl         # Model Random Forest serialisasi pickle
â”‚   â”œâ”€â”€ confusion_matrix.png            # Visualisasi confusion matrix
â”‚   â”œâ”€â”€ feature_importance.png          # Visualisasi feature importance
â”‚   â”œâ”€â”€ eda_korelasi_fitur.png          # Visualisasi korelasi fitur
â”‚   â”œâ”€â”€ eda_distribusi_fitur.png        # Visualisasi distribusi fitur
â”‚   â”œâ”€â”€ hasil_evaluasi.json             # Metrik evaluasi lengkap format JSON
â”‚   â”œâ”€â”€ laporan_duplikasi_dataset.json  # Metadata duplikasi dan burst
â”‚   â”œâ”€â”€ laporan_klasifikasi.txt         # Laporan ringkas klasifikasi
â”‚   â””â”€â”€ grayscale/                      # 200 citra grayscale 8-bit
â””â”€â”€ src/
    â”œâ”€â”€ ekstraksi_rgb.py                # Script ekstraksi 9 fitur RGB
    â”œâ”€â”€ konversi_grayscale.py           # Script konversi grayscale 8-bit
    â”œâ”€â”€ ekstraksi_glcm.py               # Script ekstraksi 5 fitur GLCM
    â”œâ”€â”€ pembuatan_csv.py                # Script penggabungan fitur ke CSV utama
    â”œâ”€â”€ klasifikasi.py                  # Script pelatihan Random Forest & evaluasi
    â””â”€â”€ buat_notebook.py               # Script generator notebook
```

### Eksekusi Seluruh Pipeline:
```bash
cd src
python ekstraksi_rgb.py
python konversi_grayscale.py
python ekstraksi_glcm.py
python pembuatan_csv.py
python klasifikasi.py
```

### Eksekusi Jupyter Notebook:
```bash
cd notebooks
jupyter notebook klasifikasi_citra_sepatu.ipynb
```
