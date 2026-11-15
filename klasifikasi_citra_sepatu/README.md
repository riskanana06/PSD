# Proyek PCD: Klasifikasi Citra Susunan Sepatu Rapi dan Berantakan

Proyek ini adalah implementasi tugas mata kuliah **Pengolahan Citra Digital (PCD)** untuk melakukan klasifikasi citra susunan sepatu ke dalam dua kategori: **Rapi** dan **Berantakan** menggunakan kombinasi fitur statistik warna RGB, fitur tekstur GLCM (Gray-Level Co-occurrence Matrix), dan pengklasifikasi Random Forest.

---

## 1. Deskripsi & Tujuan Proyek

- **Objek Klasifikasi:** Susunan sepatu (bukan ruangan atau objek lain).
- **Kategori:** 
  - `rapi` (100 citra)
  - `berantakan` (100 citra)
- **Total Dataset:** 200 citra dalam format JPG, JPEG, dan HEIC.
- **Tujuan:**
  1. Mengekstraksi 9 fitur statistik warna RGB (Mean, Standard Deviation, Skewness per channel R, G, B).
  2. Mengonversi citra ke grayscale 8-bit.
  3. Mengekstraksi 5 fitur tekstur GLCM (Energy, Entropy, Contrast, Correlation, Homogeneity).
  4. Menggabungkan 14 fitur numerik ke dalam satu dataset CSV utama (`dataset_fitur_citra.csv`).
  5. Mencegah *data leakage* menggunakan pengelompokan duplikasi citra (MD5 + dHash).
  6. Melakukan klasifikasi menggunakan algoritma Random Forest dan mengevaluasi hasilnya.

---

## 2. Struktur Direktori Proyek

```text
klasifikasi_citra_sepatu/
├── README.md                           # Dokumentasi proyek (file ini)
├── .mplconfig/                         # Cache matplotlib
├── notebooks/
│   └── klasifikasi_citra_sepatu.ipynb  # Jupyter Notebook alur klasifikasi lengkap
├── output/
│   ├── dataset_fitur_citra.csv         # Dataset final (200 baris × 15 kolom)
│   ├── fitur_rgb_sementara.csv         # Hasil ekstraksi 9 fitur RGB
│   ├── fitur_glcm_sementara.csv        # Hasil ekstraksi 5 fitur GLCM
│   ├── model_random_forest.pkl         # Model Random Forest (pickle)
│   ├── confusion_matrix.png            # Visualisasi confusion matrix
│   ├── feature_importance.png          # Visualisasi feature importance
│   ├── hasil_evaluasi.json             # Evaluasi metrik dalam format JSON
│   ├── laporan_duplikasi_dataset.json  # Metadata duplikasi dan identifikasi burst
│   ├── laporan_duplikasi_dataset.txt   # Ringkasan teks duplikasi dataset
│   ├── laporan_glcm.txt                # Laporan ekstraksi GLCM
│   ├── laporan_grayscale.txt           # Laporan konversi grayscale
│   ├── laporan_klasifikasi.txt         # Laporan performa klasifikasi Random Forest
│   ├── metadata_glcm.json              # Metadata rinci ekstraksi GLCM
│   └── grayscale/                      # 200 citra grayscale 8-bit
│       ├── rapi/                       # 100 citra grayscale kategori rapi
│       └── berantakan/                 # 100 citra grayscale kategori berantakan
└── src/
    ├── ekstraksi_rgb.py                # Script ekstraksi fitur warna RGB
    ├── konversi_grayscale.py           # Script konversi citra ke grayscale 8-bit
    ├── ekstraksi_glcm.py               # Script ekstraksi fitur tekstur GLCM
    ├── pembuatan_csv.py                # Script penggabungan fitur ke CSV final
    ├── klasifikasi.py                  # Script pemodelan Random Forest & evaluasi
    ├── preprocessing.py                # Script pembacaan dan audit citra awal
    └── buat_notebook.py               # Generator notebook otomatis
```

---

## 3. Fitur yang Diekstraksi

### A. 9 Fitur Statistik Warna RGB
Dihitung dari citra RGB asli:
1. `mean_R`: Rata-rata intensitas kanal merah
2. `mean_G`: Rata-rata intensitas kanal hijau
3. `mean_B`: Rata-rata intensitas kanal biru
4. `std_R`: Standar deviasi kanal merah
5. `std_G`: Standar deviasi kanal hijau
6. `std_B`: Standar deviasi kanal biru
7. `skew_R`: Kemencengan distribusi kanal merah
8. `skew_G`: Kemencengan distribusi kanal hijau
9. `skew_B`: Kemencengan distribusi kanal biru

### B. 5 Fitur Tekstur GLCM
Dihitung dari citra grayscale 8-bit menggunakan `skimage.feature.graycomatrix` dan `graycoprops` dengan parameter:
- Jarak: `[1]`
- Sudut: `[0, pi/4, pi/2, 3*pi/4]` (0°, 45°, 90°, 135°)
- Level: `256`
- Simetris: `True`, Normalisasi: `True`
- Hasil akhir: rata-rata dari keempat sudut

Fitur:
1. `energy`: Keseragaman intensitas tekstur
2. `entropy`: Kompleksitas / keacakan tekstur (dihitung manual $- \sum P \log_2 P$)
3. `contrast`: Variasi kontras lokal intensitas piksel tetangga
4. `correlation`: Ketergantungan linier intensitas piksel tetangga
5. `homogeneity`: Homogenitas / kedekatan distribusi elemen terhadap diagonal

---

## 4. Pencegahan Data Leakage & Pembagian Data

- **Metode Pengelompokan:** Pemeriksaan duplikasi citra menggunakan hash MD5 (file identik) dan dHash 64-bit dengan jarak Hamming $\le 5$ (kemiripan visual/burst).
- **Connected Components (Union-Find):** Menghasilkan 177 kelompok citra independen.
- **Pembagian Data:** `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=14)`
  - **Training:** 162 citra (81%) — 83 rapi, 79 berantakan
  - **Testing:** 38 citra (19%) — 17 rapi, 21 berantakan
  - **Kebocoran data (Data Leakage):** 0 kelompok yang terpecah antara training dan testing.

---

## 5. Hasil Pelatihan & Evaluasi Random Forest

- **Hyperparameter:** `RandomForestClassifier(n_estimators=100, random_state=14)`
- **Akurasi:** **71,05%** (27 dari 38 citra testing benar)
- **Macro Precision:** **72,12%**
- **Macro Recall:** **69,33%**
- **Macro F1-Score:** **69,33%**

### Detail per Kelas:
- **Rapi:** Precision = 75,00%, Recall = 52,94%, F1 = 62,07% (Support = 17)
- **Berantakan:** Precision = 69,23%, Recall = 85,71%, F1 = 76,60% (Support = 21)

### Confusion Matrix:
- True Positive (`rapi` diprediksi `rapi`): **9**
- False Negative (`rapi` diprediksi `berantakan`): **8**
- False Positive (`berantakan` diprediksi `rapi`): **3**
- True Negative (`berantakan` diprediksi `berantakan`): **18**

### 5 Fitur Paling Berpengaruh (Feature Importance):
1. `skew_G` (9,12%)
2. `std_R` (9,08%)
3. `correlation` (8,69%)
4. `skew_B` (8,60%)
5. `contrast` (7,82%)

---

## 6. Cara Menjalankan Program

### Menjalankan Seluruh Alur Script:
```bash
cd src
python ekstraksi_rgb.py
python konversi_grayscale.py
python ekstraksi_glcm.py
python pembuatan_csv.py
python klasifikasi.py
```

### Menjalankan Jupyter Notebook:
```bash
cd notebooks
jupyter notebook klasifikasi_citra_sepatu.ipynb
```

