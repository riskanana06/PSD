# Ekstraksi 68 Fitur TSFEL

Tahap ekstraksi fitur (*feature extraction*) dilakukan untuk mengubah data deret waktu CO, NO₂, dan SO₂ menjadi representasi numerik. Ekstraksi dilakukan menggunakan pustaka **TSFEL** (*Time Series Feature Extraction Library*).

Setiap polutan diekstraksi menjadi 68 fitur sehingga keseluruhan data menghasilkan:

$$
68 \times 3 = 204 \text{ fitur}
$$

## 1. Domain Ekstraksi Fitur

Fitur TSFEL yang digunakan berasal dari beberapa domain berikut:

- **Statistical Features:** Menjelaskan distribusi nilai sinyal, seperti mean, median, skewness, kurtosis, variansi, dan standar deviasi.
- **Temporal Features:** Menjelaskan perubahan sinyal berdasarkan waktu, seperti autokorelasi, zero crossing, slope, dan turning point.
- **Spectral Features:** Menjelaskan karakteristik sinyal dalam domain frekuensi menggunakan transformasi Fourier.
- **Fractal Features:** Menjelaskan tingkat kompleksitas dan pola perubahan sinyal.

## 2. Hasil Ekstraksi Fitur

Ekstraksi dilakukan terhadap ketiga polutan dengan hasil:

| Polutan | Jumlah Baris | Jumlah Fitur |
|---|---:|---:|
| CO | 1 | 68 |
| NO₂ | 1 | 68 |
| SO₂ | 1 | 68 |
| Gabungan | 1 | 204 |

File hasil ekstraksi yang dihasilkan adalah:

- `CO_AsemRowo_TSFEL_68_Clean.csv`
- `NO2_AsemRowo_TSFEL_68_Clean.csv`
- `SO2_AsemRowo_TSFEL_68_Clean.csv`
- `AsemRowo_TSFEL_204_Clean.csv`

Untuk keperluan PCA dan K-Means, ekstraksi juga dilakukan menggunakan sistem window sehingga diperoleh 49 baris dan 204 fitur.

## 3. Fitur Spectral Decrease dan Spectral Distance

Berdasarkan pembagian fitur ekstraksi, fitur yang dibahas pada bagian ini adalah:

1. `spectral_decrease(signal, fs)`
2. `spectral_distance(signal, fs)`

Kedua fitur termasuk dalam domain spectral dan dihitung berdasarkan magnitudo hasil transformasi Fourier.

## 4. Contoh Sinyal

Contoh perhitungan manual menggunakan sinyal:

$$
x=[1,2,3,4]
$$

Frekuensi sampling:

$$
f_s=1
$$

Magnitudo *Real Fast Fourier Transform* (RFFT) dari sinyal tersebut adalah:

$$
A=[10,\ 2.828427,\ 2]
$$

## 5. Spectral Decrease

### 5.1 Pengertian

Spectral decrease mengukur besarnya penurunan amplitudo spektrum dari komponen frekuensi pertama menuju komponen frekuensi berikutnya.

Nilai yang semakin negatif menunjukkan penurunan amplitudo spektrum yang semakin besar.

### 5.2 Rumus

$$
SD=
\frac{
\displaystyle\sum_{k=1}^{M-1}
\frac{A_k-A_0}{k}
}{
\displaystyle\sum_{k=1}^{M-1}A_k
}
$$

Keterangan:

- $A_0$ adalah amplitudo FFT pertama.
- $A_k$ adalah amplitudo FFT pada indeks ke-$k$.
- $M$ adalah jumlah komponen FFT.

### 5.3 Perhitungan Manual

Diketahui:

$$
A=[10,\ 2.828427,\ 2]
$$

Hitung pembilang:

$$
\frac{2.828427-10}{1}
+
\frac{2-10}{2}
$$

$$
=-7.171573-4
$$

$$
=-11.171573
$$

Hitung penyebut:

$$
2.828427+2=4.828427
$$

Maka:

$$
SD=\frac{-11.171573}{4.828427}
$$

$$
SD=-2.313708
$$

## 6. Spectral Distance

### 6.1 Pengertian

Spectral distance mengukur jarak antara *cumulative sum* magnitudo FFT dan garis linear yang dibentuk dari nol hingga nilai *cumulative sum* terakhir.

Fitur ini menunjukkan seberapa jauh distribusi energi frekuensi menyimpang dari distribusi linear.

### 6.2 Rumus

*Cumulative sum* magnitudo FFT:

$$
C_k=\sum_{i=0}^{k}A_i
$$

Garis linear pembanding:

$$
L_k=\frac{k}{M-1}C_{M-1}
$$

Spectral distance:

$$
D=\sum_{k=0}^{M-1}(L_k-C_k)
$$

### 6.3 Perhitungan Manual

*Cumulative sum* dari magnitudo FFT adalah:

$$
C=[10,\ 12.828427,\ 14.828427]
$$

Garis linear pembanding adalah:

$$
L=[0,\ 7.414214,\ 14.828427]
$$

Selisih garis linear dengan *cumulative sum*:

$$
L-C=[-10,\ -5.414213,\ 0]
$$

Maka:

$$
D=-10-5.414213+0
$$

$$
D=-15.414213
$$

## 7. Pembuktian Menggunakan TSFEL

Kode berikut digunakan untuk membuktikan hasil perhitungan manual:

```python
import numpy as np

from tsfel.feature_extraction.features import (
    spectral_decrease,
    spectral_distance,
)

signal = np.array([1, 2, 3, 4], dtype=float)
fs = 1

fft_magnitude = np.abs(np.fft.rfft(signal))

print("Magnitudo FFT:", fft_magnitude)
print("Spectral decrease:", spectral_decrease(signal, fs))
print("Spectral distance:", spectral_distance(signal, fs))
```

Hasil program:

```text
Magnitudo FFT: [10.          2.82842712  2.        ]
Spectral decrease: -2.313708
Spectral distance: -15.414214
```

Hasil perhitungan TSFEL sama dengan hasil perhitungan manual. Dengan demikian, perhitungan kedua fitur berhasil dibuktikan.

## 8. Penerapan pada Data Polutan Asem Rowo

Kode berikut digunakan untuk menghitung kedua fitur pada data CO, NO₂, dan SO₂:

```python
from pathlib import Path

import pandas as pd
from tsfel.feature_extraction.features import (
    spectral_decrease,
    spectral_distance,
)

folder = Path(__file__).parent
fs = 1

data_polutan = {
    "CO": "CO_AsemRowo_Timeseries_Clean.csv",
    "NO2": "NO2_AsemRowo_Timeseries_Clean.csv",
    "SO2": "SO2_AsemRowo_Timeseries_Clean.csv",
}

hasil = []

for polutan, nama_file in data_polutan.items():
    df = pd.read_csv(folder / nama_file)
    sinyal = df[polutan].astype(float).to_numpy()

    hasil.append(
        {
            "polutan": polutan,
            "spectral_decrease": spectral_decrease(sinyal, fs),
            "spectral_distance": spectral_distance(sinyal, fs),
        }
    )

df_hasil = pd.DataFrame(hasil)
print(df_hasil)
```

Hasil ekstraksi kedua fitur adalah:

| Polutan | Spectral Decrease | Spectral Distance |
|---|---:|---:|
| CO | -7.450080 | -1238.463923 |
| NO₂ | -2.896352 | -2.793965 |
| SO₂ | -1.172661 | -22.046128 |

## 9. Interpretasi Hasil

CO mempunyai nilai spectral decrease paling negatif, yaitu `-7.450080`. Hal ini menunjukkan amplitudo spektrum CO mengalami penurunan yang lebih besar dibandingkan NO₂ dan SO₂.

CO juga mempunyai spectral distance dengan magnitudo paling besar, yaitu `-1238.463923`. Hal ini menunjukkan *cumulative spectrum* CO memiliki penyimpangan paling besar terhadap garis linear pembanding.

Perbedaan nilai ketiga polutan menunjukkan bahwa CO, NO₂, dan SO₂ mempunyai karakteristik distribusi frekuensi yang berbeda.