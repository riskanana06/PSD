# 68 Fitur TSFEL

Tahap ekstraksi fitur (*feature extraction*) dilakukan untuk mengubah deret waktu mentah $\text{NO}_2$ menjadi representasi numerik yang menangkap karakteristik domain statistik, temporal, dan spektral menggunakan pustaka **TSFEL** (*Time Series Feature Extraction Library*).

---

## 1. Domain Ekstraksi Fitur

Ekstraksi fitur TSFEL mencakup tiga kelompok domain utama:

* **Statistical Features:** Menangkap distribusi nilai polutan, seperti mean, median, skewness, kurtosis, dan standar deviasi.
* **Temporal Features:** Mengukur pola ketergantungan waktu, autokorelasi, zero-crossing rate, serta dinamika perubahan sinyal.
* **Spectral Features:** Menganalisis karakteristik frekuensi melalui transformasi Fourier, energi spektral, dan spectral roll-off.

---

## 2. Kode Ekstraksi Fitur (Python)

Kode berikut digunakan untuk memproses file deret waktu bersih `NO2_AsemRowo_daily_clean.csv` menjadi 68 fitur:

```python
import pandas as pd
import tsfel

# 1. Muat dataset deret waktu bersih
df = pd.read_csv("NO2_AsemRowo_daily_clean.csv")

# 2. Ambil konfigurasi domain fitur lengkap
cfg = tsfel.get_features_by_domain()

# 3. Ekstraksi 68 fitur dari data NO2
fitur_tsfel = tsfel.time_series_features_extractor(cfg, df["value"], fs=1)

# 4. Simpan ke berkas CSV
fitur_tsfel.to_csv("NO2_AsemRowo_TSFEL_68.csv", index=False)
print(f"Total fitur yang dihasilkan: {fitur_tsfel.shape[1]} kolom")