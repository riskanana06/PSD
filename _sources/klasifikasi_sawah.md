# Klasifikasi Lahan Jawa Timur

Penelitian ini menggunakan citra Sentinel-2A untuk mengklasifikasikan lokasi sampel di Jawa Timur menjadi enam kelas lahan. Prosesnya meliputi pengumpulan data, penyaringan piksel, ekstraksi fitur, pembagian data, perbandingan model, evaluasi, dan visualisasi peta.

Kode pada halaman ini merupakan potongan dari script pengolahan yang digunakan. Setiap potongan saling berhubungan dengan konfigurasi dan fungsi pada script aslinya. Hasil yang ditampilkan merupakan hasil pengolahan yang sudah diperoleh.

## Alur Penelitian

Menentukan tujuan dan kelas lahan → Membuat polygon sampel → Mengunduh citra Sentinel-2A → Menyaring piksel → Menghitung fitur → Membagi training dan testing berdasarkan polygon → Membandingkan model → Memilih model terbaik → Melakukan testing → Menampilkan peta → Membahas kaitan hasil dengan kebijakan.

## 1. Tujuan Analisis

Analisis ini bertujuan mengklasifikasikan lokasi sampel lahan di Jawa Timur menjadi enam kelas, yaitu sawah, bangunan, mangrove, lahan hijau, laut, dan danau.

Analisis penggunaan lahan (*land use*) membantu memahami pemanfaatan suatu wilayah, misalnya untuk pertanian dan kawasan terbangun. Klasifikasi penutup lahan (*land cover classification*) membedakan karakteristik permukaan berdasarkan informasi citra satelit.

Hasil penelitian dapat menjadi informasi awal untuk pembahasan perlindungan lahan pertanian, pelestarian mangrove, pemanfaatan ruang, dan perlindungan badan air.

## 2. Data Understanding

### 2.1 Wilayah dan Kelas

Wilayah kajian adalah Provinsi Jawa Timur. Sampel disimpan dalam file `PSD_6_Kelas_Gabungan.geojson`.

Setiap polygon memiliki `sample_id` sebagai identitas dan `kelas` sebagai label acuan.

| Kelas | Pengertian dalam penelitian | Jumlah Polygon |
|---|---|---:|
| Sawah | Lahan pertanian sawah | 30 |
| Bangunan | Kawasan dengan bangunan atau permukaan terbangun | 30 |
| Mangrove | Vegetasi mangrove di kawasan pesisir | 30 |
| Lahan Hijau | Vegetasi selain sampel sawah dan mangrove | 30 |
| Laut | Perairan laut terbuka | 30 |
| Danau | Badan air danau atau ranu | 30 |
| **Total** | **Enam kelas** | **180** |

Kelas lahan hijau merupakan kelompok umum. Pada penelitian ini, lahan hijau belum dipisahkan menjadi hutan, semak, kebun, atau kelompok vegetasi lainnya.

### 2.2 Acuan Klasifikasi Lahan Indonesia

Acuan pembahasan klasifikasi penutup lahan adalah **SNI 7645-1:2014 tentang Klasifikasi Penutup Lahan — Bagian 1: Skala Kecil dan Menengah**, yang diterbitkan oleh Badan Standardisasi Nasional.

Enam kelas dalam penelitian ini merupakan pengelompokan operasional sesuai kebutuhan tugas. Pengelompokan tersebut bukan salinan lengkap seluruh kelas dan hierarki SNI.

### 2.3 Sumber dan Periode Citra

Data citra menggunakan **Sentinel-2A Level-2A** dari **Copernicus Data Space Ecosystem**.

Periode pencarian citra adalah **1 Juni sampai 30 September 2026**. Tanggal citra dapat berbeda antarpolygon karena pemilihan dilakukan berdasarkan lokasi dan ketersediaan citra.

Persentase awan pada tile dipertimbangkan ketika memilih citra. Setelah pengunduhan, kondisi piksel di dalam polygon diperiksa kembali karena persentase awan tile belum tentu sama dengan kondisi pada lokasi sampel.

## 3. Pengumpulan Data

Pengumpulan data dilakukan dengan langkah berikut:

1. Membaca GeoJSON berisi 180 polygon berlabel.
2. Mencari citra Sentinel-2A Level-2A.
3. Mengurutkan kandidat citra berdasarkan persentase awan.
4. Mengunduh 12 layer melalui Process API.
5. Memeriksa piksel valid di dalam polygon.
6. Menyimpan citra dalam TIFF dan metadata dalam JSON.
7. Menyimpan laporan status pengunduhan.

### 3.1 Konfigurasi Pengunduhan

Potongan kode berikut berasal dari `unduh_sentinel_semua.py`.

```python
ROOT = Path(__file__).resolve().parent
GEOJSON = ROOT / "PSD_6_Kelas_Gabungan.geojson"
OUTPUT = ROOT / "citra_sentinel"

BASE = "https://sh.dataspace.copernicus.eu"
TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu"
    "/auth/realms/CDSE/protocol/openid-connect/token"
)

PERIODE = "2026-06-01T00:00:00Z/2026-09-30T23:59:59Z"

BANDS = [
    "B02", "B03", "B04", "B05", "B06",
    "B07", "B08", "B8A", "B11", "B12",
    "SCL", "dataMask"
]
```

`GEOJSON` menunjukkan lokasi polygon sampel, sedangkan `OUTPUT` menentukan folder penyimpanan citra. `PERIODE` menentukan rentang pencarian dan `BANDS` menentukan layer yang diunduh.

### 3.2 Pengaturan Layer Keluaran

```python
EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: [{bands: %s}],
    output: {
      bands: 12,
      sampleType: "FLOAT32"
    }
  };
}
function evaluatePixel(s) {
  return [
    s.B02, s.B03, s.B04, s.B05, s.B06,
    s.B07, s.B08, s.B8A, s.B11, s.B12,
    s.SCL, s.dataMask
  ];
}
""" % json.dumps(BANDS)
```

`EVALSCRIPT` mengatur citra keluaran agar memiliki 12 layer, yaitu 10 band reflektansi, SCL, dan dataMask.

### 3.3 Pencarian Citra Sentinel-2A

```python
def cari_citra(api, sampel):
    pencarian = {
        "collections": ["sentinel-2-l2a"],
        "bbox": list(sampel.geometry.iloc[0].bounds),
        "datetime": PERIODE,
        "limit": 100,
    }

    kandidat = {}
    halaman_dibaca = set()

    while True:
        hasil = api.post(
            "/catalog/v1/search", pencarian
        ).json()

        for item in hasil.get("features", []):
            platform = str(
                item.get("properties", {}).get("platform", "")
            ).lower()

            if (
                platform == "sentinel-2a"
                or item["id"].startswith("S2A")
            ):
                kandidat[item["id"]] = item

        berikutnya = hasil.get("context", {}).get("next")

        if berikutnya is None:
            break

        penanda = json.dumps(berikutnya)

        if penanda in halaman_dibaca:
            raise RuntimeError(
                "Halaman katalog berulang; pencarian dihentikan."
            )

        halaman_dibaca.add(penanda)
        pencarian["next"] = berikutnya

    return sorted(
        kandidat.values(),
        key=lambda item: (
            item["properties"].get("eo:cloud_cover", 100)
            if item["properties"].get("eo:cloud_cover") is not None
            else 100,
            item["properties"]["datetime"],
            item["id"],
        ),
    )
```

Fungsi `cari_citra()` mencari citra sesuai lokasi polygon dan periode penelitian. Kandidat dibatasi pada Sentinel-2A, kemudian diurutkan berdasarkan persentase awan, tanggal, dan identitas citra.

Objek `api` berasal dari kelas pengelola akses API pada script pengunduhan. Client ID dan Client Secret dimasukkan ketika script dijalankan.

### 3.4 Penyimpanan Progres

```python
pd.DataFrame(catatan).to_csv(
    OUTPUT / "status_unduhan.csv",
    index=False,
    encoding="utf-8-sig",
)
```

Progres disimpan setelah setiap sampel diproses. File yang sudah tersedia dan lolos pemeriksaan dapat digunakan kembali ketika script dijalankan ulang.

**Hasil pengumpulan data:** seluruh **180 sampel citra** berhasil tersedia dalam folder `citra_sentinel`.

## 4. Band Sentinel-2A

Sentinel-2 memiliki 13 band spektral dengan resolusi spasial asli yang berbeda.

| Band | Jenis Spektral | Resolusi Asli | Keterangan |
|---|---|---:|---|
| B01 | Coastal aerosol | 60 m | Informasi aerosol dan pesisir |
| B02 | Blue | 10 m | Pantulan spektrum biru |
| B03 | Green | 10 m | Pantulan spektrum hijau |
| B04 | Red | 10 m | Pantulan merah untuk analisis vegetasi |
| B05 | Red edge 1 | 20 m | Karakteristik vegetasi |
| B06 | Red edge 2 | 20 m | Karakteristik vegetasi |
| B07 | Red edge 3 | 20 m | Karakteristik vegetasi |
| B08 | Near infrared | 10 m | Pantulan inframerah dekat |
| B8A | Narrow near infrared | 20 m | Inframerah dekat dengan rentang lebih sempit |
| B09 | Water vapour | 60 m | Informasi uap air |
| B10 | Cirrus | 60 m | Deteksi cirrus; tidak tersedia sebagai band reflektansi permukaan Level-2A |
| B11 | Shortwave infrared 1 | 20 m | Karakteristik kelembapan dan permukaan |
| B12 | Shortwave infrared 2 | 20 m | Karakteristik kelembapan dan permukaan |

Band reflektansi yang digunakan adalah **B02, B03, B04, B05, B06, B07, B08, B8A, B11, dan B12**.

Citra diunduh pada grid 10 meter dalam koordinat UTM. Band beresolusi asli 20 meter diresampling ke grid tersebut. Resampling tidak menambah detail spasial asli band.

Dua layer tambahan digunakan untuk pemeriksaan kualitas:

| Layer | Fungsi |
|---|---|
| SCL | Menyaring piksel berdasarkan kelas kualitas |
| dataMask | Menunjukkan ketersediaan data pada piksel |

SCL dan dataMask digunakan untuk penyaringan, bukan sebagai fitur model.

## 5. Penyaringan Piksel

Piksel yang digunakan harus:

- Berada di dalam polygon sampel.
- Memiliki `dataMask = 1`.
- Memiliki nilai band yang valid.
- Tidak termasuk kelas SCL yang dikeluarkan.

Kelas SCL yang dikeluarkan adalah **0, 1, 3, 8, 9, 10, dan 11**, yang mencakup no data, piksel rusak atau jenuh, bayangan awan, awan, cirrus, serta salju atau es.

### 5.1 Kode Penyaringan

Potongan kode berikut berasal dari fungsi `ekstraksi()` dalam `ekstraksi_fitur_sentinel.py`.

```python
with rasterio.open(lokasi) as src:
    if src.count != 12 or src.crs is None:
        raise RuntimeError(
            "Jumlah layer atau CRS TIFF tidak sesuai."
        )

    if list(src.descriptions) != LAYERS:
        raise RuntimeError(
            "Nama atau urutan layer TIFF tidak sesuai."
        )

    polygon = sampel.to_crs(src.crs).geometry.iloc[0]

    di_dalam = geometry_mask(
        [polygon.__geo_interface__],
        out_shape=(src.height, src.width),
        transform=src.transform,
        invert=True,
    )

    nilai = src.read().astype(np.float64)

    tersedia = nilai[11] == 1

    bersih = ~np.isin(
        nilai[10], [0, 1, 3, 8, 9, 10, 11]
    )

    angka_valid = np.isfinite(nilai[:10]).all(axis=0)

    valid = di_dalam & tersedia & bersih & angka_valid

    jumlah_bersih = int(valid.sum())
    jumlah_polygon = int(di_dalam.sum())

    if jumlah_bersih == 0:
        raise RuntimeError(
            "Tidak ada piksel bersih dalam polygon."
        )

    tabel = pd.DataFrame(
        nilai[:10, valid].T,
        columns=BANDS,
    )
```

Polygon terlebih dahulu disesuaikan dengan CRS citra. Setelah itu, mask polygon digabungkan dengan pemeriksaan dataMask, SCL, dan nilai band.

Hasilnya berupa tabel yang setiap barisnya mewakili satu piksel bersih dengan 10 nilai band reflektansi.

## 6. Ekstraksi Fitur

Model menggunakan **13 fitur per piksel**, yaitu 10 band reflektansi dan tiga indeks spektral.

| Kelompok | Fitur |
|---|---|
| Band reflektansi | B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12 |
| Indeks spektral | NDVI, NDWI, NDBI |

### 6.1 NDVI

NDVI (*Normalized Difference Vegetation Index*) menggunakan band inframerah dekat dan merah.

$$
NDVI = \frac{B08-B04}{B08+B04}
$$

NDVI membantu membedakan karakteristik vegetasi.

### 6.2 NDWI

NDWI (*Normalized Difference Water Index*) pada penelitian ini menggunakan band hijau dan inframerah dekat.

$$
NDWI = \frac{B03-B08}{B03+B08}
$$

NDWI membantu mengenali badan air.

### 6.3 NDBI

NDBI (*Normalized Difference Built-up Index*) menggunakan band SWIR dan inframerah dekat.

$$
NDBI = \frac{B11-B08}{B11+B08}
$$

NDBI membantu membedakan kawasan terbangun. Nilainya juga dapat dipengaruhi tanah terbuka sehingga tidak digunakan sebagai penentu kelas secara tunggal.

### 6.4 Kode Perhitungan Indeks

```python
def indeks(a, b):
    penyebut = a + b

    return np.divide(
        a - b,
        penyebut,
        out=np.full(a.shape, np.nan, dtype=np.float64),
        where=np.abs(penyebut) > 1e-8,
    )
```

Fungsi `indeks()` digunakan untuk menghitung selisih dua band yang dibagi dengan jumlah kedua band. Penyebut yang mendekati nol menghasilkan nilai tidak valid.

Pemanggilan fungsi pada proses ekstraksi:

```python
tabel["NDVI"] = indeks(
    tabel["B08"].to_numpy(),
    tabel["B04"].to_numpy(),
)

tabel["NDWI"] = indeks(
    tabel["B03"].to_numpy(),
    tabel["B08"].to_numpy(),
)

tabel["NDBI"] = indeks(
    tabel["B11"].to_numpy(),
    tabel["B08"].to_numpy(),
)

lengkap = np.isfinite(
    tabel[FITUR].to_numpy()
).all(axis=1)

tabel = tabel.loc[lengkap].copy()
```

Setelah ketiga indeks dihitung, baris dengan fitur yang tidak valid dikeluarkan.

### 6.5 Ringkasan Statistik per Polygon

Selain dataset piksel, proses ekstraksi menghasilkan mean, median, dan standar deviasi setiap fitur per polygon.

Mean:

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i
$$

Median merupakan nilai tengah setelah data diurutkan. Jika jumlah data genap, median merupakan rata-rata dua nilai tengah.

Standar deviasi menggunakan pembagi $n$:

$$
\sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2}
$$

Keterangan:

- $x_i$: nilai fitur pada piksel ke-$i$.
- $n$: jumlah piksel valid.
- $\bar{x}$: rata-rata nilai fitur.
- $\sigma$: standar deviasi.

Kode perhitungan:

```python
for nama in FITUR:
    ringkasan[f"{nama}_mean"] = float(
        tabel[nama].mean()
    )

    ringkasan[f"{nama}_median"] = float(
        tabel[nama].median()
    )

    ringkasan[f"{nama}_std"] = float(
        tabel[nama].std(ddof=0)
    )
```

Statistik dihitung dari seluruh piksel dengan fitur valid sebelum pembatasan jumlah piksel.

Model dalam penelitian ini dilatih menggunakan **13 fitur per piksel**, bukan ringkasan statistik polygon.

### 6.6 Pembatasan Piksel

Setiap polygon diambil maksimal 500 piksel agar polygon berukuran besar tidak mendominasi jumlah data.

```python
if len(tabel) > MAKS_PIKSEL:
    tabel = tabel.sample(
        n=MAKS_PIKSEL,
        random_state=SEED,
    )

tabel = tabel.reset_index(drop=True)
tabel.insert(0, "kelas", kelas)
tabel.insert(0, "sample_id", sid)

ringkasan["piksel_diambil"] = len(tabel)
```

`MAKS_PIKSEL` bernilai 500 dan `SEED` bernilai 42. Jumlah yang diambil dapat lebih sedikit jika piksel valid dalam polygon kurang dari 500.

## 7. Hasil Ekstraksi

### 7.1 Penyimpanan Dataset

```python
dataset = pd.concat(
    tabel_piksel,
    ignore_index=True,
)

ringkasan = pd.DataFrame(tabel_polygon)

dataset.to_csv(
    OUTPUT / "dataset_piksel_sentinel.csv",
    index=False,
    encoding="utf-8-sig",
)

ringkasan.to_csv(
    OUTPUT / "fitur_polygon_sentinel.csv",
    index=False,
    encoding="utf-8-sig",
)
```

Dataset piksel disimpan dalam `dataset_piksel_sentinel.csv`. Ringkasan statistik polygon disimpan dalam `fitur_polygon_sentinel.csv`.

### 7.2 Jumlah Data yang Diperoleh

Seluruh **180 polygon** berhasil diekstraksi.

| Kelas | Jumlah Polygon | Jumlah Piksel Diambil |
|---|---:|---:|
| Sawah | 30 | 9.927 |
| Bangunan | 30 | 4.685 |
| Mangrove | 30 | 9.509 |
| Lahan Hijau | 30 | 6.160 |
| Laut | 30 | 2.983 |
| Danau | 30 | 8.353 |
| **Total** | **180** | **41.617** |

Jumlah fitur per piksel adalah **13** dan jumlah missing value pada fitur adalah **0**.

Jumlah polygon tiap kelas seimbang, tetapi jumlah piksel berbeda karena ukuran polygon dan ketersediaan piksel valid berbeda.

### 7.3 Pemeriksaan Missing Value

```python
print(
    "Jumlah baris dataset piksel:",
    len(dataset),
)

print(
    "Jumlah fitur per piksel:",
    len(FITUR),
)

print(
    "Missing pada fitur:",
    int(dataset[FITUR].isna().sum().sum()),
)
```

Ringkasan hasil:

| Pemeriksaan | Hasil |
|---|---:|
| Jumlah baris dataset piksel | 41.617 |
| Jumlah fitur per piksel | 13 |
| Missing value pada fitur | 0 |

## 8. Pembagian Training dan Testing

Pembagian menggunakan **80% training** dan **20% testing** berdasarkan polygon, dengan stratifikasi kelas dan `random_state = 42`.

Seluruh piksel dari satu polygon masuk ke kelompok yang sama.

### 8.1 Kode Pembagian Data

Potongan kode berikut berasal dari `klasifikasi_sentinel.py`.

```python
polygon = (
    data[["sample_id", "kelas"]]
    .drop_duplicates()
    .sort_values("sample_id")
    .reset_index(drop=True)
)

poly_train, poly_test = train_test_split(
    polygon,
    test_size=0.2,
    stratify=polygon["kelas"],
    random_state=SEED,
)

poly_train = poly_train.reset_index(drop=True)
poly_test = poly_test.reset_index(drop=True)

train = data[
    data["sample_id"].isin(
        poly_train["sample_id"]
    )
].copy()

test = data[
    data["sample_id"].isin(
        poly_test["sample_id"]
    )
].copy()

assert set(train["sample_id"]).isdisjoint(
    test["sample_id"]
)
```

Program membagi daftar polygon terlebih dahulu, kemudian memilih piksel sesuai ID polygon training dan testing.

`isdisjoint()` memastikan tidak ada ID polygon yang masuk ke kedua kelompok.

### 8.2 Hasil Pembagian Polygon

| Kelas | Total Polygon | Training | Testing |
|---|---:|---:|---:|
| Sawah | 30 | 24 | 6 |
| Bangunan | 30 | 24 | 6 |
| Mangrove | 30 | 24 | 6 |
| Lahan Hijau | 30 | 24 | 6 |
| Laut | 30 | 24 | 6 |
| Danau | 30 | 24 | 6 |
| **Total** | **180** | **144** | **36** |

### 8.3 Hasil Pembagian Piksel

| Kelompok | Jumlah Polygon | Jumlah Piksel |
|---|---:|---:|
| Training | 144 | 33.440 |
| Testing | 36 | 8.177 |
| **Total** | **180** | **41.617** |

Pembagian berdasarkan polygon mencegah piksel dari polygon yang sama masuk ke training dan testing. Namun, pembagian berdasarkan identitas polygon belum menjamin lokasi training dan testing berjauhan secara spasial.

## 9. Eksperimen Model

Tiga model yang dibandingkan adalah:

1. Random Forest.
2. Extra Trees.
3. Hist Gradient Boosting.

### 9.1 Kode Model Kandidat

```python
def model_kandidat():
    return {
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=SEED,
        ),

        "Extra Trees": ExtraTreesClassifier(
            n_estimators=200,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=SEED,
        ),

        "Hist Gradient Boosting": HistGradientBoostingClassifier(
            max_iter=120,
            max_leaf_nodes=15,
            learning_rate=0.1,
            l2_regularization=1.0,
            early_stopping=False,
            random_state=SEED,
        ),
    }
```

Random Forest dan Extra Trees menggunakan 200 pohon. Jumlah pohon merupakan pengaturan model, bukan jumlah sampel.

Extra Trees merupakan gabungan banyak pohon keputusan dengan pemilihan pemisahan yang diacak. Model ini berbeda dari satu Decision Tree.

### 9.2 Pembobotan Polygon

Setiap polygon dibuat memiliki total bobot yang sama ketika pelatihan.

```python
def bobot_polygon(tabel):
    jumlah = (
        tabel.groupby("sample_id")["sample_id"]
        .transform("size")
        .to_numpy()
    )

    bobot = 1.0 / jumlah

    return bobot / bobot.mean()
```

Piksel pada polygon yang memiliki banyak piksel memperoleh bobot per piksel lebih kecil. Dengan cara ini, polygon besar tidak mendominasi pelatihan.

### 9.3 Prediksi pada Tingkat Polygon

Prediksi polygon ditentukan dari rata-rata probabilitas kelas seluruh piksel sampelnya.

$$
\bar{p}_{g,c} =
\frac{1}{n_g}
\sum_{i=1}^{n_g}p_{i,c}
$$

$$
\hat{y}_g =
\operatorname{argmax}_{c}
\bar{p}_{g,c}
$$

Keterangan:

- $g$: polygon.
- $c$: kelas.
- $n_g$: jumlah piksel sampel pada polygon.
- $p_{i,c}$: probabilitas kelas $c$ untuk piksel $i$.
- $\hat{y}_g$: kelas prediksi polygon.

Kode:

```python
def prediksi_polygon(model, tabel):
    probabilitas = model.predict_proba(
        tabel[FITUR]
    )

    hasil = pd.DataFrame(
        probabilitas,
        columns=model.classes_,
    )

    hasil.insert(
        0,
        "sample_id",
        tabel["sample_id"].to_numpy(),
    )

    rata = hasil.groupby(
        "sample_id",
        sort=True,
    ).mean()

    label = tabel.groupby(
        "sample_id"
    )["kelas"].first()

    return pd.DataFrame({
        "sample_id": rata.index,
        "kelas_asli": label.reindex(
            rata.index
        ).to_numpy(),
        "kelas_prediksi": rata.idxmax(
            axis=1
        ).to_numpy(),
        "probabilitas_tertinggi": rata.max(
            axis=1
        ).to_numpy(),
    })
```

Kelas dengan rata-rata probabilitas paling tinggi dipilih sebagai hasil prediksi polygon.

### 9.4 Validasi Silang Tiga Fold

Validasi dilakukan pada **144 polygon training**. Data testing belum digunakan pada tahap pemilihan model.

```python
splitter = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=SEED,
)

folds = list(
    splitter.split(
        poly_train,
        poly_train["kelas"],
    )
)

hasil_fold = []
kandidat = model_kandidat()

for nama, template in kandidat.items():
    for nomor, (idx_train, idx_valid) in enumerate(
        folds, 1
    ):
        id_train = poly_train.iloc[
            idx_train
        ]["sample_id"]

        id_valid = poly_train.iloc[
            idx_valid
        ]["sample_id"]

        bagian_train = train[
            train["sample_id"].isin(id_train)
        ]

        bagian_valid = train[
            train["sample_id"].isin(id_valid)
        ]

        assert set(id_train).isdisjoint(id_valid)

        model = clone(template)

        model.fit(
            bagian_train[FITUR],
            bagian_train["kelas"],
            sample_weight=bobot_polygon(
                bagian_train
            ),
        )

        pred_piksel = model.predict(
            bagian_valid[FITUR]
        )

        pred_poly = prediksi_polygon(
            model,
            bagian_valid,
        )

        metrik_poly = ukuran(
            pred_poly["kelas_asli"],
            pred_poly["kelas_prediksi"],
        )

        hasil_fold.append({
            "model": nama,
            "fold": nomor,
            "accuracy_polygon": metrik_poly["accuracy"],
            "macro_f1_polygon": metrik_poly["macro_f1"],
            "accuracy_piksel": float(
                accuracy_score(
                    bagian_valid["kelas"],
                    pred_piksel,
                )
            ),
        })
```

Setiap model diuji menggunakan pembagian fold yang sama. Untuk setiap fold, model dilatih ulang pada bagian training fold dan dievaluasi pada bagian validasi fold.

Fungsi `ukuran()` yang digunakan untuk menghitung metrik ditampilkan pada bagian evaluasi.

## 10. Perbandingan dan Pemilihan Model

### 10.1 Kode Perbandingan Model

```python
fold_table = pd.DataFrame(hasil_fold)

perbandingan = (
    fold_table.groupby("model")
    .agg(
        cv_accuracy_polygon=(
            "accuracy_polygon", "mean"
        ),
        cv_accuracy_polygon_std=(
            "accuracy_polygon", "std"
        ),
        cv_macro_f1_polygon=(
            "macro_f1_polygon", "mean"
        ),
        cv_accuracy_piksel=(
            "accuracy_piksel", "mean"
        ),
    )
    .reset_index()
    .sort_values(
        [
            "cv_accuracy_polygon",
            "cv_macro_f1_polygon",
            "model",
        ],
        ascending=[False, False, True],
    )
)

perbandingan.to_csv(
    OUTPUT / "perbandingan_model.csv",
    index=False,
    encoding="utf-8-sig",
)
```

Model diurutkan berdasarkan rata-rata accuracy polygon. Jika nilainya sama, macro F1 polygon digunakan sebagai pembanding berikutnya.

### 10.2 Hasil Validasi Silang

| Model | Rata-rata Accuracy Polygon | Standar Deviasi Accuracy | Macro F1 Polygon | Accuracy Piksel |
|---|---:|---:|---:|---:|
| Extra Trees | 79,86% | 4,34 poin persentase | 0,796857 | 75,00% |
| Random Forest | 79,86% | 4,34 poin persentase | 0,796596 | 75,08% |
| Hist Gradient Boosting | 78,47% | 2,41 poin persentase | 0,782172 | 74,51% |

Extra Trees dan Random Forest memperoleh rata-rata accuracy polygon yang sama.

**Extra Trees dipilih karena macro F1 polygon sedikit lebih tinggi.**

Hasil tersebut menunjukkan model terbaik di antara konfigurasi yang dicoba berdasarkan kriteria pemilihan penelitian ini.

### 10.3 Pelatihan Ulang Model Terpilih

```python
terbaik = perbandingan.iloc[0]["model"]

model = clone(kandidat[terbaik])

model.fit(
    train[FITUR],
    train["kelas"],
    sample_weight=bobot_polygon(train),
)
```

Model terpilih dilatih ulang menggunakan seluruh data training. Setelah itu, model dievaluasi pada data testing.

## 11. Hasil Testing

### 11.1 Kode Perhitungan Metrik

```python
def ukuran(y, prediksi):
    return {
        "accuracy": float(
            accuracy_score(y, prediksi)
        ),
        "balanced_accuracy": float(
            balanced_accuracy_score(y, prediksi)
        ),
        "macro_f1": float(
            f1_score(
                y,
                prediksi,
                average="macro",
                zero_division=0,
            )
        ),
    }
```

Pemanggilan pada data testing:

```python
pred_piksel = model.predict(
    test[FITUR]
)

pred_poly = prediksi_polygon(
    model,
    test,
)

metrik_piksel = ukuran(
    test["kelas"],
    pred_piksel,
)

metrik_poly = ukuran(
    pred_poly["kelas_asli"],
    pred_poly["kelas_prediksi"],
)
```

Evaluasi dihitung pada dua unit yang berbeda, yaitu piksel dan polygon.

### 11.2 Evaluasi Polygon

Hasil model Extra Trees pada 36 polygon testing:

| Metrik | Hasil |
|---|---:|
| Accuracy polygon | 83,33% |
| Macro F1 polygon | 0,8302 |
| Polygon benar | 30 |
| Polygon salah | 6 |

Rumus accuracy:

$$
Accuracy =
\frac{\text{Jumlah prediksi benar}}
{\text{Jumlah sampel uji}}
$$

Dalam persen:

$$
Accuracy =
\frac{30}{36}\times100\%
=83{,}33\%
$$

### 11.3 Evaluasi Piksel

| Metrik | Hasil |
|---|---:|
| Jumlah piksel testing | 8.177 |
| Accuracy piksel | 81,67% |
| Balanced accuracy piksel | 77,24% |
| Macro F1 piksel | 0,7921 |

Rumus precision:

$$
Precision = \frac{TP}{TP+FP}
$$

Rumus recall:

$$
Recall = \frac{TP}{TP+FN}
$$

Rumus F1:

$$
F1 =
\frac{2\times Precision\times Recall}
{Precision+Recall}
$$

Keterangan untuk setiap kelas:

- $TP$: sampel kelas tersebut yang diprediksi dengan benar.
- $FP$: sampel kelas lain yang diprediksi sebagai kelas tersebut.
- $FN$: sampel kelas tersebut yang diprediksi sebagai kelas lain.

Macro F1 merupakan rata-rata F1 seluruh kelas tanpa pembobotan jumlah sampel:

$$
Macro\ F1 =
\frac{1}{K}\sum_{c=1}^{K}F1_c
$$

Balanced accuracy merupakan rata-rata recall seluruh kelas:

$$
Balanced\ Accuracy =
\frac{1}{K}\sum_{c=1}^{K}Recall_c
$$

Pada penelitian ini, $K=6$.

### 11.4 Kode Pembuatan Confusion Matrix

```python
def simpan_laporan(y, prediksi, kelas, nama):
    report = classification_report(
        y,
        prediksi,
        labels=kelas,
        output_dict=True,
        zero_division=0,
    )

    pd.DataFrame(report).T.to_csv(
        OUTPUT / f"classification_report_{nama}.csv",
        encoding="utf-8-sig",
    )

    fig, ax = plt.subplots(figsize=(9, 7))

    ConfusionMatrixDisplay.from_predictions(
        y,
        prediksi,
        labels=kelas,
        ax=ax,
        cmap="Blues",
        xticks_rotation=35,
        colorbar=False,
    )

    ax.set_title(
        f"Confusion Matrix Testing ({nama})"
    )
    ax.set_xlabel("Kelas prediksi")
    ax.set_ylabel("Kelas asli")

    fig.tight_layout()

    fig.savefig(
        OUTPUT / f"confusion_matrix_{nama}.png",
        dpi=180,
    )

    plt.close(fig)
```

Fungsi ini menyimpan classification report dalam CSV dan confusion matrix dalam PNG.

### 11.5 Confusion Matrix Polygon

```{figure} _static/confusion_matrix_polygon.png
:width: 90%
:align: center

Confusion matrix model Extra Trees pada 36 polygon testing.
```

Baris menunjukkan kelas acuan dan kolom menunjukkan kelas prediksi.

Angka diagonal menunjukkan prediksi benar. Angka di luar diagonal menunjukkan kesalahan klasifikasi.

Sebanyak **30 polygon** diprediksi dengan benar dan **enam polygon** diprediksi sebagai kelas lain.

### 11.6 Confusion Matrix Piksel

```{figure} _static/confusion_matrix_piksel.png
:width: 90%
:align: center

Confusion matrix model Extra Trees pada 8.177 piksel testing.
```

Accuracy piksel sebesar **81,67%**, balanced accuracy sebesar **77,24%**, dan macro F1 sebesar **0,7921**.

Accuracy piksel berbeda dari accuracy polygon karena unit evaluasinya berbeda.

### 11.7 Penyimpanan Model

```python
joblib.dump(
    {
        "model": model,
        "fitur": FITUR,
        "kelas": kelas,
        "nama_model": terbaik,
        "seed": SEED,
        "versi_sklearn": sklearn.__version__,
        "training_sample_ids": (
            poly_train["sample_id"].tolist()
        ),
        "testing_sample_ids": (
            poly_test["sample_id"].tolist()
        ),
    },
    OUTPUT / "model_terbaik.joblib",
)
```

Model beserta informasi fitur, kelas, dan pembagian polygon disimpan agar dapat digunakan untuk membuat peta dan menjalankan aplikasi Streamlit.

## 12. Peta Hasil Klasifikasi

Peta menampilkan hasil prediksi pada **180 polygon sampel** di Jawa Timur.

Warna menunjukkan kelas prediksi. Penanda oranye menunjukkan enam polygon testing yang salah diklasifikasikan.

### 12.1 Kode Pembuatan Peta

Potongan berikut berasal dari `buat_peta_hasil.py`.

```python
peta = folium.Map(
    location=[-7.7, 112.8],
    zoom_start=8,
    tiles=None,
    control_scale=True,
    prefer_canvas=True,
)

folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google Hybrid",
    name="Google Hybrid (dengan label)",
    overlay=False,
    show=True,
    max_zoom=20,
).add_to(peta)

folium.TileLayer(
    tiles="Esri.WorldImagery",
    name="Esri Satellite (online)",
    overlay=False,
    show=False,
).add_to(peta)

for kelas in WARNA:
    tambah_layer_kelas(
        peta,
        features,
        kelas,
    )
```

Peta menggunakan Google Hybrid sebagai latar utama dan Esri Satellite sebagai pilihan alternatif.

Fungsi `tambah_layer_kelas()` dalam script peta menambahkan polygon sesuai kelas prediksinya.

Cakupan peta disesuaikan dengan seluruh koordinat sampel:

```python
seluruh_titik = [
    titik
    for feature in features
    for titik in koordinat(
        feature["geometry"]
    )
]

bounds = [
    [
        min(p[1] for p in seluruh_titik),
        min(p[0] for p in seluruh_titik),
    ],
    [
        max(p[1] for p in seluruh_titik),
        max(p[0] for p in seluruh_titik),
    ],
]

peta.fit_bounds(
    bounds,
    padding=(25, 25),
)
```

`fit_bounds()` mengatur cakupan peta agar seluruh sebaran sampel dapat terlihat.

### 12.2 Peta Interaktif

```{raw} html
<iframe
  src="_static/peta_klasifikasi_sentinel.html"
  title="Peta hasil klasifikasi lahan Jawa Timur"
  width="100%"
  height="750"
  style="border: 1px solid #ddd; border-radius: 8px;"
  loading="lazy"
  allowfullscreen>
</iframe>
```

[Buka peta dalam halaman penuh](https://riskanana06.github.io/PSD/_static/peta_klasifikasi_sentinel.html).

Cara membaca peta:

1. Pilih layer kelas melalui kontrol di kanan atas.
2. Klik polygon untuk melihat informasi sampel dan hasil prediksi.
3. Aktifkan **Sorot Data Uji** untuk melihat polygon testing.
4. Aktifkan **Salah Klasifikasi Testing** untuk melihat kesalahan prediksi.
5. Perbesar atau perkecil peta untuk memeriksa lokasi sampel.

Peta menunjukkan lokasi sampel penelitian. Peta ini belum merupakan klasifikasi seluruh permukaan Provinsi Jawa Timur.

### 12.3 Ringkasan Prediksi pada Peta

| Kelas Prediksi | Jumlah Polygon |
|---|---:|
| Sawah | 30 |
| Bangunan | 32 |
| Mangrove | 32 |
| Lahan Hijau | 28 |
| Laut | 28 |
| Danau | 30 |
| **Total** | **180** |

Jumlah pada tabel merupakan hasil prediksi seluruh polygon sampel, termasuk training dan testing. Penilaian kemampuan model tetap mengacu pada data testing yang terpisah.

Jumlah polygon tidak menunjukkan persentase luas penutup lahan Jawa Timur.

## 13. Analisis terhadap Kebijakan Penggunaan Lahan

Acuan tata ruang wilayah kajian adalah **Peraturan Daerah Provinsi Jawa Timur Nomor 10 Tahun 2023 tentang Rencana Tata Ruang Wilayah Provinsi Jawa Timur Tahun 2023–2043**.

Klasifikasi citra menunjukkan karakteristik permukaan, sedangkan kebijakan tata ruang mengatur peruntukan ruang. Karena itu, hasil klasifikasi perlu dibandingkan dengan peta kebijakan sebelum digunakan untuk menilai kesesuaian pemanfaatan lokasi.

### 13.1 Sawah dan Perlindungan Lahan Pertanian

Model memprediksi 30 polygon sebagai sawah.

Kelas sawah berkaitan dengan **Undang-Undang Nomor 41 Tahun 2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan beserta perubahannya**.

Identifikasi sawah dapat membantu menyediakan informasi awal tentang lokasi lahan pertanian. Namun, prediksi sawah belum otomatis menunjukkan status Lahan Pertanian Pangan Berkelanjutan atau LP2B. Status tersebut membutuhkan data penetapan resmi.

Jumlah prediksi sawah yang sama dengan jumlah label acuan juga tidak berarti seluruh polygon sawah diprediksi dengan benar. Kesalahan antarkelas dapat saling mengimbangi jumlahnya.

### 13.2 Bangunan dan Pemanfaatan Ruang

Model memprediksi 32 polygon sebagai bangunan, sedangkan label acuan bangunan berjumlah 30 polygon.

Selisih tersebut menunjukkan perbedaan prediksi terhadap label pada kumpulan sampel. Selisih ini belum membuktikan pembangunan baru atau alih fungsi lahan karena analisis perubahan memerlukan pengamatan lokasi yang sama pada waktu berbeda.

Penilaian kesesuaian kawasan terbangun memerlukan peta pola ruang dan ketentuan pada lokasi tersebut.

### 13.3 Mangrove dan Ekosistem Pesisir

Model memprediksi 32 polygon sebagai mangrove.

Kelas ini berkaitan dengan **Peraturan Pemerintah Nomor 27 Tahun 2025 tentang Perlindungan dan Pengelolaan Ekosistem Mangrove**.

Pemetaan mangrove dapat menjadi informasi awal untuk inventarisasi dan pemeriksaan vegetasi pesisir. Jumlah prediksi yang lebih tinggi belum menunjukkan peningkatan luas mangrove karena yang dihitung adalah polygon sampel.

### 13.4 Lahan Hijau

Model memprediksi 28 polygon sebagai lahan hijau.

Kelas ini menggabungkan vegetasi selain sawah dan mangrove. Pengelompokan belum membedakan hutan, kebun, semak, atau ruang terbuka hijau.

Polygon lahan hijau belum otomatis merupakan kawasan lindung atau ruang terbuka hijau resmi. Penilaian tersebut memerlukan klasifikasi yang lebih rinci dan peta peruntukan ruang.

### 13.5 Laut dan Danau

Model memprediksi 28 polygon sebagai laut dan 30 polygon sebagai danau.

Untuk danau, acuan yang relevan adalah **Peraturan Menteri PUPR Nomor 28/PRT/M/2015 tentang Penetapan Garis Sempadan Sungai dan Garis Sempadan Danau**.

Polygon sampel danau belum menunjukkan keseluruhan batas danau atau garis sempadan resmi.

Untuk laut, hasil klasifikasi menunjukkan karakteristik permukaan berupa perairan. Hasil tersebut belum menentukan zonasi maupun kegiatan yang diizinkan pada ruang laut.

### 13.6 Batas Analisis Kebijakan

Accuracy polygon testing sebesar **83,33%** menunjukkan bahwa model masih memiliki kesalahan.

Penelitian ini belum melakukan overlay dengan peta RTRW, RDTR, LP2B, fungsi ekosistem mangrove, atau sempadan danau.

Karena itu, analisis yang disajikan merupakan pembahasan hubungan hasil klasifikasi dengan kebijakan. Penelitian ini belum menetapkan kepatuhan hukum pada masing-masing lokasi sampel.

## 14. File Pengolahan

| File | Fungsi |
|---|---|
| `PSD_6_Kelas_Gabungan.geojson` | Polygon sampel dan label acuan |
| `unduh_sentinel_semua.py` | Pengunduhan citra Sentinel-2A |
| `ekstraksi_fitur_sentinel.py` | Penyaringan piksel dan ekstraksi fitur |
| `klasifikasi_sentinel.py` | Pembagian data, perbandingan model, dan evaluasi |
| `buat_peta_hasil.py` | Pembuatan peta hasil klasifikasi |
| `app.py` | Aplikasi Streamlit |
| `requirements.txt` | Daftar paket Python untuk aplikasi |
| `hasil_ekstraksi/dataset_piksel_sentinel.csv` | Dataset 13 fitur per piksel |
| `hasil_ekstraksi/fitur_polygon_sentinel.csv` | Ringkasan statistik fitur per polygon |
| `hasil_klasifikasi/perbandingan_model.csv` | Hasil perbandingan model |
| `hasil_klasifikasi/prediksi_peta_polygon.csv` | Prediksi seluruh polygon sampel |
| `hasil_klasifikasi/hasil_prediksi_polygon.geojson` | Geometri beserta hasil prediksi |
| `hasil_klasifikasi/hasil_evaluasi.json` | Ringkasan evaluasi |
| `hasil_klasifikasi/model_terbaik.joblib` | Model terpilih dan informasi fitur |
| `_static/confusion_matrix_polygon.png` | Gambar evaluasi polygon |
| `_static/confusion_matrix_piksel.png` | Gambar evaluasi piksel |
| `_static/peta_klasifikasi_sentinel.html` | Peta interaktif untuk web statis |

## 15. Deployment Sistem Informasi

Sistem informasi dibuat menggunakan **Streamlit** dan dideploy melalui **Streamlit Community Cloud**.

[Buka aplikasi klasifikasi lahan di Streamlit](https://riska-klasifikasi-lahan-jatim.streamlit.app/).

### 15.1 Bagian Aplikasi

| Tab | Isi |
|---|---|
| Eksplorasi Data | Distribusi kelas, ringkasan dataset, missing value, dan statistik fitur |
| Peta Spasial | Peta hasil klasifikasi, filter kelas, dan penanda kesalahan testing |
| Model Extra Trees | Pembagian data, perbandingan model, metrik evaluasi, dan confusion matrix |
| Prediksi Data Baru | Form input reflektansi 10 band Sentinel-2A |

### 15.2 Kode Pembagian Tab

Potongan kode berikut berasal dari `app.py`.

```python
tab1, tab2, tab3, tab4 = st.tabs([
    "Eksplorasi Data",
    "Peta Spasial",
    "Model Extra Trees",
    "Prediksi Data Baru",
])
```

Empat tab digunakan agar pengguna dapat melihat data, peta, evaluasi, dan prediksi secara terpisah.

### 15.3 Kode Penayangan Peta

Pada tab peta, objek peta dibuat menggunakan fungsi `buat_peta()` lalu ditampilkan sebagai HTML.

```python
peta, _ = buat_peta(
    features,
    nama_model,
    benar,
    len(testing),
)

components.html(
    peta.get_root().render(),
    height=800,
    scrolling=True,
)
```

Variabel `features` berisi polygon yang sesuai dengan filter kelas pilihan pengguna.

### 15.4 Prediksi Data Baru

Pengguna memasukkan nilai reflektansi 10 band Sentinel-2A. Aplikasi menghitung NDVI, NDWI, dan NDBI secara otomatis sehingga model tetap menerima 13 fitur.

Nilai awal form merupakan median fitur dataset sebagai contoh pengisian. Nilai tersebut dapat diganti dengan reflektansi piksel citra yang ingin diprediksi.

Hasil form berlaku untuk **satu piksel**. Prediksi polygon pada peta menggunakan rata-rata probabilitas piksel sampelnya.

Probabilitas prediksi pada form berbeda dari accuracy testing.

### 15.5 Hubungan Web Statis dan Streamlit

Web statis Jupyter Book memuat proses pengumpulan data, penjelasan band, kode pengolahan, ekstraksi fitur, pembagian data, perbandingan model, hasil evaluasi, dan peta.

Aplikasi Streamlit menyediakan tampilan interaktif serta form prediksi data baru menggunakan model yang telah dilatih.

## 16. Kesimpulan

Penelitian menggunakan 180 polygon sampel yang terdiri dari enam kelas lahan di Jawa Timur.

Ekstraksi menghasilkan **41.617 piksel**, dengan **13 fitur per piksel** dan **0 missing value pada fitur**.

Pembagian data dilakukan berdasarkan polygon, yaitu **144 polygon training** dan **36 polygon testing**.

Dari tiga model yang dibandingkan, **Extra Trees** dipilih berdasarkan hasil validasi silang pada data training. Accuracy polygon testing mencapai **83,33%**, yaitu **30 dari 36 polygon** diprediksi dengan benar.

Hasil penelitian ditampilkan melalui peta interaktif dan aplikasi Streamlit. Hasil ini dapat menjadi informasi awal untuk pembahasan penggunaan lahan, tetapi penilaian kesesuaian kebijakan membutuhkan data kebijakan spasial dan verifikasi lebih lanjut.

## 17. Referensi

1. Badan Standardisasi Nasional. **SNI 7645-1:2014, Klasifikasi Penutup Lahan — Bagian 1: Skala Kecil dan Menengah**. [Katalog BSN](https://pesta.bsn.go.id/produk/by_ics/5?ics_no=07&key=).

2. Copernicus Data Space Ecosystem. [Sentinel-2 Level-2A](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html).

3. Copernicus Data Space Ecosystem. [Sentinel-2 Level-1C](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L1C.html).

4. Scikit-learn. [Ensemble Methods](https://scikit-learn.org/1.6/modules/ensemble.html).

5. Pemerintah Provinsi Jawa Timur. [Perda Nomor 10 Tahun 2023 tentang RTRW Provinsi Jawa Timur Tahun 2023–2043](https://jdih.jatimprov.go.id/site-pages/dokumen-populer/peraturan-daerah-provinsi-jawa-timur-nomor-10-tahun-2023-tentang-rencana-tata-ruang-wilayah-provinsi-jawa-timur-tahun-2023-2043).

6. Pemerintah Republik Indonesia. [UU Nomor 41 Tahun 2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan](https://jdih.pertanian.go.id/peraturan/uu-nomor-41-tahun-2009), beserta perubahannya.

7. Pemerintah Republik Indonesia. [PP Nomor 27 Tahun 2025 tentang Perlindungan dan Pengelolaan Ekosistem Mangrove](https://jdih.kemenkopangan.go.id/peraturan-pemerintah-nomor-27-tahun-2025-tentang-perlindungan-dan-pengelolaan-ekosistem-mangrove).

8. Kementerian PUPR. [Permen PUPR Nomor 28/PRT/M/2015 tentang Penetapan Garis Sempadan Sungai dan Garis Sempadan Danau](https://peraturan.go.id/id/permen-pupr-no-28-prt-m-2015-tahun-2015).