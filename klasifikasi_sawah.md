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

Data sampel dibuat menggunakan QGIS dengan membagi wilayah menjadi dua kelas, yaitu sawah dan non-sawah. Setiap kelas mempunyai 50 polygon sampel sehingga total data yang digunakan adalah 100 sampel.

| Kelas | Jumlah Sampel |
|---|---:|
| Sawah | 50 |
| Non-sawah | 50 |
| Total | 100 |

Polygon sampel disimpan menggunakan format GeoJSON dan sistem koordinat EPSG:4326 atau WGS 84.

File yang digunakan adalah:

- `Sampel_sawah.geojson`
- `Sampel_Non_sawah.geojson`

## 2. Peta Interaktif Sampel

Peta berikut menampilkan persebaran sampel sawah dan non-sawah. Polygon berwarna hijau menunjukkan sampel sawah, sedangkan polygon berwarna merah menunjukkan sampel non-sawah.

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


jumlah_sawah = len(data_sawah)
jumlah_non_sawah = len(data_non_sawah)

print("Jumlah sampel sawah:", jumlah_sawah)
print("Jumlah sampel non-sawah:", jumlah_non_sawah)
print("Total sampel:", jumlah_sawah + jumlah_non_sawah)


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

<span style="
    display: inline-block;
    width: 16px;
    height: 16px;
    background: #00FF00;
    border: 1px solid #006400;
    margin-right: 6px;
"></span>
Sawah<br>

<span style="
    display: inline-block;
    width: 16px;
    height: 16px;
    background: #FF0000;
    border: 1px solid #8B0000;
    margin-right: 6px;
"></span>
Non-sawah
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

Peta dapat digeser serta diperbesar dan diperkecil. Tombol layer di bagian kanan dapat digunakan untuk menampilkan atau menyembunyikan polygon sawah dan non-sawah.

## 3. Data Sentinel-2

Citra yang digunakan berasal dari Sentinel-2 L2A tanggal 4 Oktober 2026. Citra diunduh dalam format TIFF dengan sistem koordinat WGS 84 atau EPSG:4326.

Band yang digunakan adalah:

| Band | Nama | Kegunaan |
|---|---|---|
| B02 | Blue | Mengidentifikasi karakteristik permukaan |
| B03 | Green | Mengamati pantulan vegetasi hijau |
| B04 | Red | Membedakan vegetasi dan non-vegetasi |
| B08 | Near Infrared | Mengidentifikasi tingkat kehijauan vegetasi |

Setiap polygon sampel dihitung nilai rata-rata B02, B03, B04, B08, dan NDVI.

Rumus NDVI yang digunakan adalah:

$$
NDVI = \frac{B08-B04}{B08+B04}
$$

Nilai NDVI membantu membedakan wilayah yang mempunyai vegetasi dengan wilayah non-vegetasi.

## 4. Proses Klasifikasi

Klasifikasi dilakukan menggunakan algoritma Random Forest. Data dibagi menjadi 80% data latih dan 20% data uji.

Fitur yang digunakan dalam proses klasifikasi adalah:

1. Nilai rata-rata B02.
2. Nilai rata-rata B03.
3. Nilai rata-rata B04.
4. Nilai rata-rata B08.
5. Nilai NDVI.

Model dilatih menggunakan 80 sampel, sedangkan 20 sampel lainnya digunakan untuk menguji kemampuan model dalam membedakan sawah dan non-sawah.

## 5. Hasil Klasifikasi

Hasil pengujian memperoleh akurasi sebesar **95%**.

| Kelas | Data Uji | Prediksi Benar |
|---|---:|---:|
| Non-sawah | 10 | 10 |
| Sawah | 10 | 9 |
| Total | 20 | 19 |

Dari 20 data uji, terdapat satu sampel sawah yang diprediksi sebagai non-sawah.

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

Confusion matrix menunjukkan bahwa seluruh 10 sampel non-sawah berhasil diprediksi dengan benar. Pada kelas sawah, sembilan sampel berhasil diprediksi dengan benar dan satu sampel salah diprediksi sebagai non-sawah.

## 6. Kesimpulan

Sebanyak 100 polygon sampel berhasil digunakan, yang terdiri atas 50 sampel sawah dan 50 sampel non-sawah. Seluruh polygon berhasil dipadukan dengan citra Sentinel-2 L2A.

Model Random Forest memperoleh akurasi sebesar 95%. Hasil tersebut menunjukkan bahwa kombinasi band B02, B03, B04, B08, dan NDVI dapat digunakan untuk membedakan wilayah sawah dan non-sawah.

Peta interaktif membantu menampilkan lokasi seluruh sampel secara lebih jelas. Pengguna dapat menggeser peta, memperbesar tampilan, serta menampilkan atau menyembunyikan setiap layer sampel.