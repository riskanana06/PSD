---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: "0.13"
    jupytext_version: "1.16.4"
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Klasifikasi Sawah dan Non-Sawah

## 1. Pengambilan Sampel

Data sampel dibuat menggunakan QGIS dengan membagi wilayah menjadi dua kelas, yaitu sawah dan non-sawah. Setiap kelas mempunyai 50 poligon sehingga total data yang digunakan adalah 100 sampel.

| Kelas | Label | Jumlah Sampel |
|---|---|---:|
| Sawah | `Sawah` | 50 |
| Non-sawah | `Non-sawah` | 50 |
| Total | - | 100 |

Poligon disimpan dalam format GeoJSON menggunakan sistem koordinat EPSG:4326 atau WGS 84.

File yang digunakan adalah:

- `Sampel_sawah.geojson`
- `Sampel_Non_sawah.geojson`

Setiap poligon dianggap sebagai satu sampel. Nilai piksel Sentinel-2 yang berada di dalam poligon digunakan untuk menghitung nilai rata-rata setiap band.

Oleh karena itu, 50 poligon sawah menghasilkan 50 baris sampel sawah, bukan 50 piksel.

## 2. Peta Interaktif Sampel

Peta berikut menampilkan persebaran 50 sampel sawah dan 50 sampel non-sawah. Poligon hijau menunjukkan sawah, sedangkan poligon merah menunjukkan non-sawah.

```{code-cell} ipython3
:tags: [hide-input]

from pathlib import Path

import folium
import geopandas as gpd
from folium.plugins import MeasureControl


folder = Path.cwd()

file_sawah = folder / "Sampel_sawah.geojson"
file_non_sawah = folder / "Sampel_Non_sawah.geojson"


if not file_sawah.exists():
    raise FileNotFoundError(
        f"File tidak ditemukan: {file_sawah}"
    )

if not file_non_sawah.exists():
    raise FileNotFoundError(
        f"File tidak ditemukan: {file_non_sawah}"
    )


data_sawah = gpd.read_file(
    file_sawah
).to_crs(epsg=4326)

data_non_sawah = gpd.read_file(
    file_non_sawah
).to_crs(epsg=4326)


print(
    "Jumlah sampel sawah:",
    len(data_sawah),
)

print(
    "Jumlah sampel non-sawah:",
    len(data_non_sawah),
)

print(
    "Total sampel:",
    len(data_sawah) + len(data_non_sawah),
)


batas_sawah = data_sawah.total_bounds
batas_non_sawah = data_non_sawah.total_bounds

barat = min(
    batas_sawah[0],
    batas_non_sawah[0],
)

selatan = min(
    batas_sawah[1],
    batas_non_sawah[1],
)

timur = max(
    batas_sawah[2],
    batas_non_sawah[2],
)

utara = max(
    batas_sawah[3],
    batas_non_sawah[3],
)

pusat_peta = [
    (selatan + utara) / 2,
    (barat + timur) / 2,
]


peta = folium.Map(
    location=pusat_peta,
    zoom_start=12,
    tiles=None,
)


folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="Citra Satelit",
    overlay=False,
    control=True,
    show=True,
).add_to(peta)


def gaya_sawah(_):
    return {
        "fillColor": "#00FF00",
        "color": "#006400",
        "weight": 2,
        "fillOpacity": 0.60,
    }


def gaya_non_sawah(_):
    return {
        "fillColor": "#FF0000",
        "color": "#8B0000",
        "weight": 2,
        "fillOpacity": 0.60,
    }


def gaya_sorotan(_):
    return {
        "weight": 4,
        "fillOpacity": 0.85,
    }


folium.GeoJson(
    data_sawah.to_json(),
    name="50 Sampel Sawah",
    style_function=gaya_sawah,
    highlight_function=gaya_sorotan,
    tooltip=folium.GeoJsonTooltip(
        fields=["FID", "label"],
        aliases=["ID:", "Kelas:"],
        sticky=False,
    ),
).add_to(peta)


folium.GeoJson(
    data_non_sawah.to_json(),
    name="50 Sampel Non-sawah",
    style_function=gaya_non_sawah,
    highlight_function=gaya_sorotan,
    tooltip=folium.GeoJsonTooltip(
        fields=["FID", "label"],
        aliases=["ID:", "Kelas:"],
        sticky=False,
    ),
).add_to(peta)


legenda = """
<div style="
    position: fixed;
    bottom: 35px;
    left: 35px;
    z-index: 9999;
    background-color: white;
    border: 2px solid grey;
    border-radius: 6px;
    padding: 12px;
    font-size: 14px;
">
<b>Legenda Sampel</b><br>
<span style="color:#00AA00;">■</span> Sawah<br>
<span style="color:#FF0000;">■</span> Non-sawah
</div>
"""

peta.get_root().html.add_child(
    folium.Element(legenda)
)

folium.LayerControl(
    collapsed=False
).add_to(peta)

peta.add_child(
    MeasureControl()
)

peta.fit_bounds(
    [
        [selatan, barat],
        [utara, timur],
    ],
    padding=(25, 25),
)

peta
```

Peta dapat digeser, diperbesar, dan diperkecil. Kontrol layer dapat digunakan untuk menampilkan atau menyembunyikan sampel sawah dan non-sawah.

## 3. Data Sentinel-2

Citra yang digunakan berasal dari Sentinel-2 L2A tanggal 4 Oktober 2026. Citra disimpan dalam format TIFF dengan sistem koordinat EPSG:4326.

Band yang digunakan adalah:

| Band | Nama | Kegunaan |
|---|---|---|
| B02 | Blue | Mengidentifikasi karakteristik permukaan |
| B03 | Green | Mengamati pantulan vegetasi hijau |
| B04 | Red | Membedakan vegetasi dan nonvegetasi |
| B08 | Near Infrared | Mengidentifikasi tingkat kehijauan vegetasi |

Nilai piksel B02, B03, B04, dan B08 yang berada di dalam setiap poligon dihitung nilai rata-ratanya.

## 4. Perhitungan NDVI

NDVI atau *Normalized Difference Vegetation Index* digunakan untuk mengukur tingkat kehijauan vegetasi berdasarkan band merah dan inframerah dekat.

Rumus NDVI adalah:

$$
NDVI =
\frac{B08-B04}
{B08+B04}
$$

Keterangan:

- $B08$ adalah band *Near Infrared* atau NIR.
- $B04$ adalah band merah atau *Red*.
- Nilai NDVI berada pada rentang $-1$ sampai $1$.

Interpretasi nilai NDVI adalah:

| Rentang NDVI | Interpretasi |
|---|---|
| Kurang dari 0 | Air, bayangan, atau nonvegetasi |
| 0 sampai 0,2 | Bangunan atau tanah terbuka |
| 0,2 sampai 0,5 | Vegetasi sedang |
| Lebih dari 0,5 | Vegetasi rapat dan sehat |

### 4.1 Contoh Perhitungan NDVI

Diketahui:

$$
B08=0.60
$$

$$
B04=0.20
$$

Maka:

$$
NDVI =
\frac{0.60-0.20}
{0.60+0.20}
$$

$$
NDVI =
\frac{0.40}
{0.80}
=0.50
$$

Nilai NDVI sebesar 0,50 menunjukkan adanya vegetasi yang cukup rapat.

Kode perhitungan NDVI adalah:

```python
penyebut = b08 + b04

if penyebut == 0:
    ndvi = 0
else:
    ndvi = (b08 - b04) / penyebut
```

## 5. Fitur Klasifikasi

Fitur yang digunakan dalam proses klasifikasi adalah:

1. B02
2. B03
3. B04
4. B08
5. NDVI

Jumlah fitur yang digunakan adalah:

$$
4 \text{ band} + 1 \text{ NDVI}
=
5 \text{ fitur}
$$

Struktur data klasifikasi adalah:

| Kolom | Keterangan |
|---|---|
| B02 | Rata-rata band biru dalam poligon |
| B03 | Rata-rata band hijau dalam poligon |
| B04 | Rata-rata band merah dalam poligon |
| B08 | Rata-rata band NIR dalam poligon |
| NDVI | Indeks vegetasi dari B08 dan B04 |
| kelas | Label Sawah atau Non-sawah |

## 6. Polygon Training dan Pixel Training

Dataset awal terdiri atas 100 poligon, yaitu 50 poligon sawah dan 50 poligon non-sawah.

Data dibagi menjadi 80% training dan 20% testing menggunakan stratifikasi.

| Kelas | Poligon Awal | Poligon Training | Poligon Testing |
|---|---:|---:|---:|
| Sawah | 50 | 40 | 10 |
| Non-sawah | 50 | 40 | 10 |
| Total | 100 | 80 | 20 |

Jumlah poligon training adalah:

$$
40 \text{ poligon sawah}
+
40 \text{ poligon non-sawah}
=
80 \text{ poligon training}
$$

Piksel di dalam poligon tidak dijadikan baris training secara individual. Piksel valid di dalam setiap poligon digunakan untuk menghitung nilai rata-rata band.

Alurnya adalah:

$$
\text{Piksel dalam poligon}
\rightarrow
\text{Rata-rata band}
\rightarrow
\text{Satu baris sampel}
$$

| Komponen | Jumlah atau Penggunaan |
|---|---|
| Poligon sawah training | 40 poligon |
| Poligon non-sawah training | 40 poligon |
| Total poligon training | 80 poligon |
| Piksel training individual | Tidak dijadikan baris terpisah |
| Penggunaan piksel | Dihitung rata-rata per poligon |
| Baris data training | 80 baris |
| Fitur setiap baris | B02, B03, B04, B08, dan NDVI |

Jumlah piksel pada setiap poligon dapat berbeda karena ukuran dan bentuk poligon tidak selalu sama.

## 7. Algoritma Random Forest

Klasifikasi dilakukan menggunakan **Random Forest Classifier**.

Random Forest membentuk beberapa pohon keputusan. Hasil klasifikasi akhir ditentukan berdasarkan keputusan terbanyak dari seluruh pohon tersebut.

Kode yang digunakan adalah:

```python
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


data_sampel = pd.read_csv(
    "Sampel_Sentinel2_Sawah_NonSawah.csv"
)

daftar_fitur = [
    "B02",
    "B03",
    "B04",
    "B08",
    "NDVI",
]

X = data_sampel[daftar_fitur]
y = data_sampel["kelas"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
)

model.fit(
    X_train,
    y_train,
)

hasil_prediksi = model.predict(
    X_test
)


akurasi = accuracy_score(
    y_test,
    hasil_prediksi,
)

laporan = classification_report(
    y_test,
    hasil_prediksi,
)

matriks = confusion_matrix(
    y_test,
    hasil_prediksi,
)


print("Jumlah fitur:", len(daftar_fitur))
print("Jumlah data training:", len(X_train))
print("Jumlah data testing:", len(X_test))
print("Akurasi:", akurasi)
print(laporan)
print(matriks)
```

## 8. Tampilan Data Training

Data training merupakan 80 sampel yang dipilih dari keseluruhan 100 sampel.

Kode berikut digunakan untuk menampilkan seluruh data training pada web:

```{code-cell} ipython3
:tags: [hide-input]

import pandas as pd

from sklearn.model_selection import train_test_split


data_sampel = pd.read_csv(
    "Sampel_Sentinel2_Sawah_NonSawah.csv"
)

daftar_fitur = [
    "B02",
    "B03",
    "B04",
    "B08",
    "NDVI",
]

X = data_sampel[daftar_fitur]
y = data_sampel["kelas"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


data_training = X_train.copy()
data_training["kelas"] = y_train

data_training = data_training.reset_index(
    drop=True
)

data_training.index = (
    data_training.index + 1
)

data_training.index.name = "Nomor"

pd.set_option(
    "display.max_rows",
    100,
)


print(
    "Jumlah data training:",
    len(data_training),
)

display(data_training)
```

Ringkasan data training adalah:

| Komponen | Jumlah |
|---|---:|
| Data training sawah | 40 sampel |
| Data training non-sawah | 40 sampel |
| Total data training | 80 sampel |
| Jumlah fitur | 5 fitur |

Setiap baris data training merupakan hasil rata-rata piksel dalam satu poligon.

## 9. Hasil Klasifikasi

Hasil pengujian memperoleh akurasi sebesar:

$$
\text{Akurasi}
=
\frac{\text{Prediksi benar}}
{\text{Jumlah data testing}}
\times 100\%
$$

$$
\text{Akurasi}
=
\frac{19}{20}
\times 100\%
=
95\%
$$

Ringkasan hasil prediksi adalah:

| Kelas | Data Uji | Prediksi Benar | Prediksi Salah |
|---|---:|---:|---:|
| Non-sawah | 10 | 10 | 0 |
| Sawah | 10 | 9 | 1 |
| Total | 20 | 19 | 1 |

Nilai evaluasi setiap kelas adalah:

| Kelas | Precision | Recall | F1-Score |
|---|---:|---:|---:|
| Non-sawah | 0.91 | 1.00 | 0.95 |
| Sawah | 1.00 | 0.90 | 0.95 |

```{figure} _static/Confusion_Matrix_Sawah_NonSawah.png
---
width: 70%
name: confusion-matrix-sawah
---
Confusion matrix hasil klasifikasi sawah dan non-sawah.
```

Confusion matrix menunjukkan bahwa 10 sampel non-sawah diprediksi dengan benar. Pada kelas sawah, sembilan sampel diprediksi dengan benar dan satu sampel diprediksi sebagai non-sawah.

## 10. Peta Hasil Klasifikasi

Peta berikut menampilkan hasil klasifikasi sawah dan non-sawah menggunakan Random Forest.

<iframe
    src="_static/peta_klasifikasi_interaktif.html"
    width="100%"
    height="700"
    style="border: 1px solid #cccccc; border-radius: 8px;"
    loading="lazy">
</iframe>

Peta dapat digeser, diperbesar, dan diperkecil. Kontrol layer dapat digunakan untuk menampilkan atau menyembunyikan hasil klasifikasi.

Ringkasan hasil akhir adalah:

| Keterangan | Hasil |
|---|---|
| Algoritma | Random Forest Classifier |
| Poligon awal | 100 poligon |
| Poligon training | 80 poligon |
| Poligon testing | 20 poligon |
| Jumlah fitur | 5 fitur |
| Akurasi | 95% |
| Kelas | Sawah dan Non-sawah |

## 11. Kesimpulan

Sebanyak 100 poligon digunakan, terdiri atas 50 poligon sawah dan 50 poligon non-sawah.

Data training terdiri atas 80 poligon, yaitu 40 sawah dan 40 non-sawah. Data testing terdiri atas 20 poligon, yaitu 10 sawah dan 10 non-sawah.

Setiap poligon dipadukan dengan Sentinel-2 L2A untuk memperoleh rata-rata B02, B03, B04, dan B08. NDVI dihitung menggunakan B08 dan B04.

Jumlah fitur yang digunakan adalah lima fitur, yaitu B02, B03, B04, B08, dan NDVI.

Algoritma Random Forest memperoleh akurasi sebesar 95%, dengan 19 prediksi benar dari 20 data testing.

Peta sampel dan peta hasil klasifikasi ditampilkan secara interaktif agar persebaran sawah dan non-sawah dapat diamati berdasarkan lokasinya.