# Klasifikasi Citra Susunan Sepatu

Selamat datang di dokumentasi proyek **Klasifikasi Citra Susunan Sepatu Rapi dan Berantakan**. Proyek ini merupakan implementasi pengolahan citra digital (*Digital Image Processing*) dan pembelajaran mesin (*Machine Learning*) untuk mengenali dan mengklasifikasikan susunan sepatu ke dalam dua kategori: **Rapi** (*tidy*) dan **Berantakan** (*messy*).

---

## 1. Tujuan Proyek

Tujuan utama dari proyek ini adalah:
1. Mengembangkan pipeline klasifikasi citra berbasis fitur tradisional (ekstraksi fitur warna statistik dan tekstur matriks kookurensi).
2. Mengekstraksi karakteristik visual citra berupa **9 fitur statistik RGB** (Mean, Standard Deviation, dan Skewness tiap channel) dan **5 fitur tekstur GLCM** (Energy, Entropy, Contrast, Correlation, dan Homogeneity).
3. Menggabungkan kedua modalitas fitur menjadi representasi dataset berdimensi 14 fitur numerik dan 1 label target.
4. Mencegah kebocoran data (*data leakage*) melalui identifikasi kelompok duplikasi dan kemiripan visual citra (*burst/near-duplicate*) sebelum pembagian data pelatihan dan pengujian.
5. Membangun model klasifikasi **Random Forest** serta mengevaluasi performanya menggunakan akurasi, precision, recall, F1-score, dan confusion matrix.

---

## 2. Gambaran Dataset

Dataset yang digunakan berfokus spesifik pada objek **susunan sepatu**, bukan ruangan, kamar, atau objek lainnya.

| Karakteristik | Keterangan |
|---|---|
| **Jumlah Total Citra** | 200 citra |
| **Kelas Target** | 2 kelas seimbang (`rapi`: 100 citra, `berantakan`: 100 citra) |
| **Format File** | JPG, JPEG, dan HEIC (High Efficiency Image Container) |
| **Kanal Warna** | RGB (Red, Green, Blue) 3 channel |
| **Lokasi Dataset Sumber** | `PSD/rapi-20261112T014224Z-1-001/rapi` dan `PSD/berantakan-20261112T020312Z-1-001/berantakan` |

### Komposisi Format File per Kategori
- **Kategori Rapi (100 citra):** 71 file `.jpg`, 26 file `.jpeg`, 3 file `.heic`
- **Kategori Berantakan (100 citra):** 63 file `.jpg`, 34 file `.jpeg`, 3 file `.heic`

Citra dibaca menggunakan modul `Pillow` yang diintegrasikan dengan `pillow-heif` sehingga seluruh file HEIC dapat didekode secara otomatis tanpa kehilangan resolusi atau kualitas warna. Seluruh citra dikonversi ke mode warna RGB standar sebelum proses ekstraksi fitur.

---

## 3. Ekstraksi Fitur Statistik RGB (9 Fitur)

Warna merupakan karakteristik visual primer yang membedakan distribusi piksel pada susunan sepatu. Untuk setiap citra, channel warna dipisahkan menjadi tiga komponen independen: **Red ($R$)**, **Green ($G$)**, dan **Blue ($B$)**.

Dari masing-masing kanal, dihitung tiga besaran statistik deskriptif:

### 3.1 Mean (Rata-rata Intensitas Piksel)
Mean mengukur tingkat kecerahan rata-rata kanal warna pada seluruh piksel citra berukuran $M \times N$:

$$
\mu_c = \frac{1}{M \times N} \sum_{i=1}^{M} \sum_{j=1}^{N} I_c(i, j)
$$

dengan $c \in \{R, G, B\}$ dan $I_c(i, j)$ merupakan intensitas piksel pada baris $i$ dan kolom $j$.

### 3.2 Standard Deviation (Standar Deviasi)
Standar deviasi mencerminkan variasi atau kontras sebaran intensitas di sekitar nilai rata-rata:

$$
\sigma_c = \sqrt{\frac{1}{M \times N} \sum_{i=1}^{M} \sum_{j=1}^{N} (I_c(i, j) - \mu_c)^2}
$$

### 3.3 Skewness (Kemencengan Distribusi)
Skewness mengukur derajat asimetri distribusi intensitas piksel terhadap nilai rata-ratanya:

$$
\gamma_c = \frac{\frac{1}{M \times N} \sum_{i=1}^{M} \sum_{j=1}^{N} (I_c(i, j) - \mu_c)^3}{\sigma_c^3}
$$

- Nilai skewness positif ($\gamma > 0$) menunjukkan ekor distribusi memanjang ke arah intensitas terang (distribusi condong ke piksel gelap).
- Nilai skewness negatif ($\gamma < 0$) menunjukkan ekor memanjang ke arah intensitas gelap.
- Nilai mendekati 0 menunjukkan distribusi intensitas yang simetris.

### 3.4 Sembilan Fitur Warna yang Dihasilkan
1. `mean_R`: Rata-rata intensitas kanal merah.
2. `mean_G`: Rata-rata intensitas kanal hijau.
3. `mean_B`: Rata-rata intensitas kanal biru.
4. `std_R`: Standar deviasi intensitas kanal merah.
5. `std_G`: Standar deviasi intensitas kanal hijau.
6. `std_B`: Standar deviasi intensitas kanal biru.
7. `skew_R`: Kemencengan distribusi intensitas kanal merah.
8. `skew_G`: Kemencengan distribusi intensitas kanal hijau.
9. `skew_B`: Kemencengan distribusi intensitas kanal biru.

Hasil ekstraksi tahap ini disimpan dalam file sementara `fitur_rgb_sementara.csv` dengan ukuran 200 baris $\times$ 10 kolom (9 fitur + 1 label).

---

## 4. Konversi Grayscale 8-bit

Sebelum melakukan ekstraksi tekstur menggunakan GLCM, seluruh 200 citra dikonversi ke citra skala abu-abu (*grayscale*) 8-bit.

### 4.1 Spesifikasi Teknis Konversi
- **Mode Konversi:** Grayscale `L` (Pillow), menggunakan formula pembobotan luminansi standar ITU-R 601-2:
  
  $$
  Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B
  $$

- **Jumlah Channel:** 1 channel (intensitas monokrom).
- **Tipe Data:** `uint8` (unsigned integer 8-bit).
- **Rentang Nilai:** 0 hingga 255.
- **Penyimpanan:** Citra grayscale disimpan terpisah di direktori `output/grayscale/rapi/` dan `output/grayscale/berantakan/` tanpa memodifikasi file citra asli. Untuk file HEIC, hasil konversi disimpan dalam format lossless PNG 8-bit.

---

## 5. Ekstraksi Fitur Tekstur GLCM (5 Fitur)

*Gray-Level Co-occurrence Matrix* (GLCM) adalah metode analisis tekstur statistik orde kedua yang menghitung probabilitas kemunculan pasangan piksel dengan nilai intensitas tertentu pada jarak spasial dan sudut orientasi tertentu.

### 5.1 Parameter GLCM
- **Jarak Antarpiksel ($d$):** `[1]` (piksel bertetangga langsung).
- **Sudut Orientasi ($\theta$):** 4 arah mata angin:
  - $0^\circ$ (horizontal, ke kanan)
  - $45^\circ$ (diagonal kanan atas)
  - $90^\circ$ (vertikal, ke atas)
  - $135^\circ$ (diagonal kiri atas)
- **Level Intensitas Gray-Level:** `levels = 256` (resolusi penuh 8-bit).
- **Simetri:** `symmetric = True` ($P(i, j) = P(j, i)$).
- **Normalisasi:** `normed = True` ($\sum_{i} \sum_{j} P(i, j) = 1$).

Setiap fitur tekstur dihitung pada masing-masing dari keempat sudut, kemudian dirata-ratakan (*rotation invariant average*):

$$
\text{Fitur}_{\text{final}} = \frac{1}{4} \left( \text{Fitur}_{0^\circ} + \text{Fitur}_{45^\circ} + \text{Fitur}_{90^\circ} + \text{Fitur}_{135^\circ} \right)
$$

### 5.2 Lima Fitur Tekstur GLCM
Misalkan $P(i, j)$ adalah probabilitas kemunculan pasangan intensitas $i$ dan $j$:

#### 1. Energy (Uniformity / Angular Second Moment)
Mengukur keseragaman distribusi intensitas tekstur. Nilai tinggi menunjukkan tekstur yang sangat seragam atau berpola repetitif.

$$
\text{Energy} = \sqrt{\sum_{i=0}^{255} \sum_{j=0}^{255} P(i, j)^2}
$$

#### 2. Entropy
Mengukur tingkat keacakan atau kompleksitas distribusi spasial derajat keabuan. Nilai tinggi mengindikasikan tekstur yang sangat acak atau berantakan.

$$
\text{Entropy} = -\sum_{i=0}^{255} \sum_{j=0}^{255} P(i, j) \log_2 P(i, j) \quad (\text{untuk } P(i, j) > 0)
$$

#### 3. Contrast
Mengukur besarnya variasi lokal intensitas antara piksel bertetangga. Nilai kontras tinggi menunjukkan transisi derajat keabuan yang tajam (misalnya batas sepatu yang tidak teratur).

$$
\text{Contrast} = \sum_{i=0}^{255} \sum_{j=0}^{255} |i - j|^2 P(i, j)
$$

#### 4. Correlation
Mengukur ketergantungan linier nilai derajat keabuan antara piksel bertetangga.

$$
\text{Correlation} = \sum_{i=0}^{255} \sum_{j=0}^{255} \frac{(i - \mu_i)(j - \mu_j) P(i, j)}{\sigma_i \sigma_j}
$$

#### 5. Homogeneity (Inverse Difference Moment)
Mengukur kedekatan sebaran elemen GLCM terhadap diagonal utama. Nilai homogenitas tinggi menunjukkan sedikit variasi lokal antar piksel bertetangga.

$$
\text{Homogeneity} = \sum_{i=0}^{255} \sum_{j=0}^{255} \frac{P(i, j)}{1 + |i - j|^2}
$$

Hasil ekstraksi fitur tekstur disimpan dalam `fitur_glcm_sementara.csv` berukuran 200 baris $\times$ 6 kolom (5 fitur + 1 label).

---

## 6. Penggabungan Fitur Menjadi Dataset Utama (14 Fitur)

Kedua dataset sementara (RGB dan GLCM) digabungkan menjadi satu dataset utama setelah melalui validasi ketat:
1. Memverifikasi kesesuaian jumlah baris (200 baris) dan keseimbangan kelas (100 rapi, 100 berantakan).
2. Memverifikasi urutan nama file dan label citra menggunakan metadata JSON Tahap 3 dan Tahap 5 sehingga tidak ada pasangan baris yang tertukar.
3. Memastikan tidak ada nilai yang kosong (*missing value* / NaN) maupun tak hingga (*infinity*).

### 6.1 Struktur Kolom Dataset Final
Dataset utama disimpan di `klasifikasi_citra_sepatu/output/dataset_fitur_citra.csv` dengan struktur tepat 15 kolom:

```text
 1. mean_R       (float64) - Rata-rata intensitas kanal merah
 2. mean_G       (float64) - Rata-rata intensitas kanal hijau
 3. mean_B       (float64) - Rata-rata intensitas kanal biru
 4. std_R        (float64) - Standar deviasi kanal merah
 5. std_G        (float64) - Standar deviasi kanal hijau
 6. std_B        (float64) - Standar deviasi kanal biru
 7. skew_R       (float64) - Kemencengan distribusi kanal merah
 8. skew_G       (float64) - Kemencengan distribusi kanal hijau
 9. skew_B       (float64) - Kemencengan distribusi kanal biru
10. energy       (float64) - Keseragaman tekstur GLCM
11. entropy      (float64) - Kompleksitas / keacakan tekstur GLCM
12. contrast     (float64) - Variasi kontras lokal GLCM
13. correlation  (float64) - Korelasi spasial GLCM
14. homogeneity  (float64) - Homogenitas tekstur GLCM
15. label        (string)  - Label target ('rapi' atau 'berantakan')
```

> **Tautan Unduhan:**  
> Anda dapat mengunduh dataset final CSV yang sudah diekstraksi melalui tautan berikut:  
> [📥 Unduh dataset_fitur_citra.csv](_static/dataset_fitur_citra.csv)

---

## 7. Pembagian Data dan Pencegahan Data Leakage

Salah satu aspek metodologis krusial dalam klasifikasi citra adalah mencegah **kebocoran data** (*data leakage*). Kebocoran data terjadi jika citra yang berasal dari satu pengambilan foto beruntun (*burst shot*), sudut pengambilan yang hampir identik, atau salinan file masuk ke data pelatihan (*training*) dan pengujian (*testing*) sekaligus.

### 7.1 Identifikasi Duplikasi Citra
Pemeriksaan dilakukan secara sistematis pada 200 citra menggunakan dua metode:
1. **MD5 Checksum:** Mendeteksi file dengan konten biner identik (ditemukan 9 kelompok duplikasi biner).
2. **Difference Hash (dHash 64-bit):** Mendeteksi kemiripan visual (*perceptual similarity*) dengan ambang batas jarak Hamming $\le 5$ (ditemukan 6 kelompok *burst/near-duplicate*).

Seluruh pasangan duplikasi dihubungkan menggunakan struktur data *Disjoint-Set / Union-Find* sehingga membentuk **177 kelompok citra independen**.

### 7.2 Strategi Pembagian Data
Pembagian data dilakukan menggunakan `StratifiedGroupKFold` dengan parameter `n_splits = 5`, `shuffle = True`, dan `random_state = 14`. Metode ini memastikan bahwa seluruh anggota dalam satu kelompok duplikasi yang sama **hanya dialokasikan ke training atau testing saja**, dengan kebocoran data sebesar **0%**.

| Subset | Jumlah Sampel | Persentase | Distribusi Kelas |
|---|---|---|---|
| **Training Set** | 162 | 81,0% | 83 `rapi`, 79 `berantakan` |
| **Testing Set** | 38 | 19,0% | 17 `rapi`, 21 `berantakan` |
| **Total** | **200** | **100,0%** | **100 `rapi`, 100 `berantakan`** |

Proporsi ini sangat mendekati rasio teoritis 80:20 dengan tetap menjamin independensi mutlak antara data latih dan data uji.

---

## 8. Klasifikasi Random Forest

Klasifikasi dilakukan menggunakan algoritma **Random Forest Classifier**. Random Forest merupakan algoritma *ensemble learning* berbasis *Bagging* (*Bootstrap Aggregating*) yang membangun sekumpulan pohon keputusan (*decision trees*).

### 8.1 Keunggulan Random Forest untuk Fitur Warna dan Tekstur
- **Invarian terhadap penskalaan fitur:** Pohon keputusan melakukan pemisahan (*splitting*) berdasarkan ambang batas ordinal, sehingga fitur dengan rentang nilai berbeda (misalnya mean $0-255$ dan energy $0.05-0.3$) tidak memerlukan normalisasi atau standarisasi tambahan.
- **Tahan terhadap multikolinieritas:** Mampu menangani korelasi alami antarkanal warna ($R, G, B$) dan tekstur GLCM secara efektif.
- **Kemampuan estimasi Feature Importance:** Menyediakan skor signifikansi relatif fitur dalam proses klasifikasi.

### 8.2 Konfigurasi Hyperparameter
- `n_estimators = 100` (100 pohon keputusan independen).
- `criterion = 'gini'` (pengukuran ketidakmurnian Gini).
- `random_state = 14` (menjamin reprodusibilitas hasil).

---

## 9. Hasil Evaluasi Model

Model Random Forest dievaluasi menggunakan data testing independen yang terdiri atas **38 citra**.

### 9.1 Ringkasan Metrik Kinerja

| Metrik Evaluasi | Nilai | Keterangan |
|---|---|---|
| **Akurasi (Accuracy)** | **71,05%** | 27 dari 38 sampel testing berhasil diprediksi dengan benar |
| **Macro Precision** | **72,12%** | Rata-rata ketepatan prediksi antarkelas |
| **Macro Recall** | **69,33%** | Rata-rata sensitivitas deteksi antarkelas |
| **Macro F1-Score** | **69,33%** | Rata-rata harmonik precision dan recall |

### 9.2 Laporan Klasifikasi per Kelas (Classification Report)

| Kelas Target | Precision | Recall | F1-Score | Support (Jumlah Data Uji) |
|---|---|---|---|---|
| **Rapi** | **0,7500 (75,00%)** | 0,5294 (52,94%) | 0,6207 (62,07%) | 17 |
| **Berantakan** | 0,6923 (69,23%) | **0,8571 (85,71%)** | **0,7660 (76,60%)** | 21 |
| **Macro Average** | **0,7212 (72,12%)** | **0,6933 (69,33%)** | **0,6933 (69,33%)** | 38 |
| **Weighted Average** | **0,7181 (71,81%)** | **0,7105 (71,05%)** | **0,7010 (70,10%)** | 38 |

### 9.3 Confusion Matrix

Confusion matrix memperlihatkan distribusi detail antara kelas aktual dan kelas yang diprediksi oleh model.

```{figure} _static/confusion_matrix_sepatu.png
---
width: 75%
align: center
name: fig-confusion-matrix-sepatu
---
Confusion Matrix Model Random Forest pada Data Testing (38 Citra).
```

Tabel matriks kontingensi:

| Kelas Aktual \ Prediksi | Prediksi: Rapi | Prediksi: Berantakan | Total Aktual |
|---|---|---|---|
| **Aktual: Rapi** | **9** *(True Positive)* | **8** *(False Negative)* | 17 |
| **Aktual: Berantakan** | **3** *(False Positive)* | **18** *(True Negative)* | 21 |
| **Total Prediksi** | 12 | 26 | 38 |

**Interpretasi Hasil:**
- **True Positive (TP = 9):** Sebanyak 9 citra susunan sepatu rapi berhasil dikenali dengan benar sebagai rapi.
- **True Negative (TN = 18):** Sebanyak 18 citra susunan sepatu berantakan berhasil dikenali dengan benar sebagai berantakan (kemampuan deteksi kelas berantakan mencapai **85,71%**).
- **False Positive (FP = 3):** Hanya 3 citra susunan sepatu berantakan yang salah diklasifikasikan sebagai rapi.
- **False Negative (FN = 8):** Sebanyak 8 citra susunan sepatu rapi terprediksi sebagai berantakan, umumnya dipicu oleh variasi warna alas sepatu yang kontras atau sudut pandang miring yang menyerupai pola tidak teratur.

---

## 10. Analisis Kepentingan Fitur (Feature Importance)

Random Forest menghitung tingkat kepentingan fitur (*feature importance*) berdasarkan penurunan rata-rata *Gini Impurity* di seluruh pohon keputusan.

```{figure} _static/feature_importance_sepatu.png
---
width: 85%
align: center
name: fig-feature-importance-sepatu
---
Diagram Tingkat Kepentingan 14 Fitur (Warna RGB & Tekstur GLCM).
```

### Nilai Kepentingan Seluruh Fitur

| Peringkat | Fitur | Kategori | Skor Importance | Persentase Kontribusi |
|---|---|---|---|---|
| 1 | `skew_G` | Warna (RGB) | 0,0912 | 9,12% |
| 2 | `std_R` | Warna (RGB) | 0,0908 | 9,08% |
| 3 | `correlation` | Tekstur (GLCM) | 0,0869 | 8,69% |
| 4 | `skew_B` | Warna (RGB) | 0,0860 | 8,60% |
| 5 | `contrast` | Tekstur (GLCM) | 0,0782 | 7,82% |
| 6 | `mean_B` | Warna (RGB) | 0,0722 | 7,22% |
| 7 | `mean_R` | Warna (RGB) | 0,0706 | 7,06% |
| 8 | `entropy` | Tekstur (GLCM) | 0,0674 | 6,74% |
| 9 | `homogeneity`| Tekstur (GLCM) | 0,0649 | 6,49% |
| 10 | `std_B` | Warna (RGB) | 0,0630 | 6,30% |
| 11 | `mean_G` | Warna (RGB) | 0,0622 | 6,22% |
| 12 | `skew_R` | Warna (RGB) | 0,0602 | 6,02% |
| 13 | `energy` | Tekstur (GLCM) | 0,0553 | 5,53% |
| 14 | `std_G` | Warna (RGB) | 0,0511 | 5,11% |

**Temuan Utama:**
- Lima fitur paling dominan (`skew_G`, `std_R`, `correlation`, `skew_B`, `contrast`) membuktikan bahwa klasifikasi susunan sepatu memerlukan perpaduan seimbang antara informasi warna (asimetri distribusi cahaya dan variasi warna merah) serta informasi tekstur spasial (korelasi dan kontras lokal piksel tetangga).
- Tekstur GLCM `correlation` dan `contrast` berperan signifikan dalam mendeteksi keteraturan orientasi sepatu: susunan rapi cenderung memiliki korelasi spasial teratur antar pasang sepatu yang sejajar, sedangkan susunan berantakan menciptakan kontras acak pada area tumpukan sepatu.

---

## 11. Struktur Berkas dan Panduan Menjalankan Program

Seluruh kode sumber, notebook, model, dan laporan klasifikasi citra sepatu terintegrasi di dalam direktori `klasifikasi_citra_sepatu/`:

```text
klasifikasi_citra_sepatu/
├── README.md                           # Dokumentasi teknis proyek
├── .mplconfig/                         # Konfigurasi isolasi cache matplotlib
├── notebooks/
│   └── klasifikasi_citra_sepatu.ipynb  # Jupyter Notebook alur klasifikasi lengkap
├── output/
│   ├── dataset_fitur_citra.csv         # Dataset final (200 baris × 15 kolom)
│   ├── fitur_rgb_sementara.csv         # Hasil ekstraksi 9 fitur warna RGB
│   ├── fitur_glcm_sementara.csv        # Hasil ekstraksi 5 fitur tekstur GLCM
│   ├── model_random_forest.pkl         # Model Random Forest terlatih
│   ├── confusion_matrix.png            # Grafik evaluasi confusion matrix
│   ├── feature_importance.png          # Grafik evaluasi feature importance
│   ├── hasil_evaluasi.json             # Metrik evaluasi lengkap format JSON
│   ├── laporan_duplikasi_dataset.json  # Metadata & kelompok duplikasi citra
│   ├── laporan_klasifikasi.txt         # Laporan teks performa model
│   └── grayscale/                      # 200 citra hasil konversi grayscale 8-bit
│       ├── rapi/                       # 100 citra grayscale rapi
│       └── berantakan/                 # 100 citra grayscale berantakan
└── src/
    ├── ekstraksi_rgb.py                # Script ekstraksi 9 fitur RGB
    ├── konversi_grayscale.py           # Script konversi grayscale 8-bit
    ├── ekstraksi_glcm.py               # Script ekstraksi 5 fitur GLCM
    ├── pembuatan_csv.py                # Script penggabungan fitur ke CSV utama
    ├── klasifikasi.py                  # Script pemodelan Random Forest & evaluasi
    ├── preprocessing.py                # Script audit pembacaan dataset
    └── buat_notebook.py               # Generator notebook otomatis
```

### Panduan Eksekusi Script (Langkah demi Langkah)

Jika ingin menjalankan ulang pipeline dari tahap awal hingga akhir melalui terminal:

```bash
# 1. Masuk ke direktori script
cd klasifikasi_citra_sepatu/src

# 2. Ekstraksi 9 fitur statistik warna RGB
python ekstraksi_rgb.py

# 3. Konversi citra ke grayscale 8-bit
python konversi_grayscale.py

# 4. Ekstraksi 5 fitur tekstur GLCM dari citra grayscale
python ekstraksi_glcm.py

# 5. Penggabungan fitur dan pembuatan dataset CSV utama
python pembuatan_csv.py

# 6. Pembagian data, pelatihan Random Forest, dan evaluasi
python klasifikasi.py
```

### Menjalankan Jupyter Notebook
Notebook interaktif dapat dibuka langsung menggunakan Jupyter Lab, Jupyter Notebook, atau VS Code:

```bash
cd klasifikasi_citra_sepatu/notebooks
jupyter notebook klasifikasi_citra_sepatu.ipynb
```

---

## 12. Kesimpulan

1. **Keberhasilan Pipeline:** Seluruh alur kerja klasifikasi citra susunan sepatu berhasil diimplementasikan secara komprehensif dan konsisten dengan seluruh instruksi dosen, mencakup ekstraksi 9 fitur RGB, konversi grayscale 8-bit, ekstraksi 5 fitur GLCM, penggabungan menjadi 14 fitur numerik, pencegahan data leakage, dan klasifikasi Random Forest.
2. **Kinerja Model:** Model Random Forest menghasilkan akurasi sebesar **71,05%** pada data uji yang belum pernah dilihat sebelumnya (*unseen test set*), dengan Macro Precision **72,12%**, Macro Recall **69,33%**, dan F1-Score **69,33%**.
3. **Deteksi Kelas Berantakan:** Model memiliki sensitivitas yang sangat tinggi dalam mendeteksi susunan sepatu berantakan, dibuktikan dengan recall kelas berantakan mencapai **85,71%** (18 dari 21 citra berantakan terdeteksi secara akurat).
4. **Validitas Metodologis:** Tidak terjadi kebocoran data (*zero data leakage*) berkat pengelompokan citra berbasis hash dan dHash menggunakan `StratifiedGroupKFold`.

