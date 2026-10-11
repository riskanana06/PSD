import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from buat_peta_hasil import buat_peta


ROOT = Path(__file__).resolve().parent
HASIL = ROOT / "hasil_klasifikasi"
EKSTRAKSI = ROOT / "hasil_ekstraksi"
STATIC = ROOT / "_static"

DATASET = EKSTRAKSI / "dataset_piksel_sentinel.csv"
MODEL = HASIL / "model_terbaik.joblib"
EVALUASI = HASIL / "hasil_evaluasi.json"
PREDIKSI = HASIL / "prediksi_peta_polygon.csv"
PERBANDINGAN = HASIL / "perbandingan_model.csv"
GEOJSON = HASIL / "hasil_prediksi_polygon.geojson"

KELAS = [
    "Sawah",
    "Bangunan",
    "Mangrove",
    "Lahan Hijau",
    "Laut",
    "Danau",
]

BAND = [
    "B02", "B03", "B04", "B05", "B06",
    "B07", "B08", "B8A", "B11", "B12",
]

LABEL_BAND = {
    "B02": "B02 — Blue",
    "B03": "B03 — Green",
    "B04": "B04 — Red",
    "B05": "B05 — Red Edge 1",
    "B06": "B06 — Red Edge 2",
    "B07": "B07 — Red Edge 3",
    "B08": "B08 — Near Infrared",
    "B8A": "B8A — Narrow Near Infrared",
    "B11": "B11 — SWIR 1",
    "B12": "B12 — SWIR 2",
}


st.set_page_config(
    page_title="Klasifikasi LULC Jawa Timur",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def baca_csv(lokasi, waktu_modifikasi):
    return pd.read_csv(
        lokasi,
        dtype={"sample_id": str},
    )


@st.cache_data
def baca_json(lokasi, waktu_modifikasi):
    return json.loads(
        Path(lokasi).read_text(encoding="utf-8-sig")
    )


@st.cache_resource
def baca_model(lokasi, waktu_modifikasi):
    return joblib.load(lokasi)


def csv_file(lokasi):
    return baca_csv(
        str(lokasi),
        lokasi.stat().st_mtime_ns,
    )


def json_file(lokasi):
    return baca_json(
        str(lokasi),
        lokasi.stat().st_mtime_ns,
    )


def tampilkan_tabel(data):
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )


def tampilkan_gambar(nama, caption):
    lokasi = next(
        (
            file
            for file in [HASIL / nama, STATIC / nama]
            if file.exists()
        ),
        None,
    )

    if lokasi is not None:
        st.image(str(lokasi), caption=caption)
    else:
        st.info(f"Gambar belum tersedia: {nama}")


def normalized_difference(a, b):
    penyebut = a + b

    if abs(penyebut) <= 1e-8:
        raise ValueError(
            "Penyebut indeks mendekati nol. "
            "Periksa kembali nilai reflektansi."
        )

    return (a - b) / penyebut


st.title("Klasifikasi Penggunaan Lahan (LULC) Jawa Timur")
st.write("Menggunakan citra Sentinel-2A dan model Extra Trees.")


wajib = [
    DATASET,
    MODEL,
    EVALUASI,
    PREDIKSI,
    PERBANDINGAN,
    GEOJSON,
]

kurang = [
    str(file.relative_to(ROOT))
    for file in wajib
    if not file.exists()
]

if kurang:
    st.error("File yang diperlukan belum tersedia.")

    for nama in kurang:
        st.write(nama)

    st.stop()


try:
    data = csv_file(DATASET)
    prediksi = csv_file(PREDIKSI)
    perbandingan = csv_file(PERBANDINGAN)
    evaluasi = json_file(EVALUASI)
    geo = json_file(GEOJSON)

    bundle = baca_model(
        str(MODEL),
        MODEL.stat().st_mtime_ns,
    )

    model = bundle["model"]
    fitur = list(bundle["fitur"])
    nama_model = str(bundle["nama_model"])

    if set(fitur) != set(BAND + ["NDVI", "NDWI", "NDBI"]):
        raise ValueError(
            "Fitur model berbeda dari 13 fitur eksperimen."
        )

    wajib_dataset = {"sample_id", "kelas", *fitur}

    if not wajib_dataset.issubset(data.columns):
        raise ValueError("Kolom dataset tidak lengkap.")

    if data[["sample_id", "kelas"] + fitur].isna().any().any():
        raise ValueError("Dataset memiliki missing value.")

    if not np.isfinite(
        data[fitur].to_numpy(dtype=float)
    ).all():
        raise ValueError("Dataset memiliki fitur tidak valid.")

    if prediksi["sample_id"].duplicated().any():
        raise ValueError("Ada ID polygon berulang.")

    if set(data["sample_id"]) != set(prediksi["sample_id"]):
        raise ValueError(
            "ID dataset dan hasil prediksi tidak cocok."
        )

    if (
        data.groupby("sample_id")["kelas"].nunique() != 1
    ).any():
        raise ValueError(
            "Satu polygon memiliki beberapa label acuan."
        )

    label_dataset = (
        data.groupby("sample_id")["kelas"].first()
    )

    label_prediksi = (
        prediksi.set_index("sample_id")["kelas"]
    )

    if not label_dataset.reindex(
        label_prediksi.index
    ).equals(label_prediksi):
        raise ValueError(
            "Label dataset dan hasil prediksi tidak cocok."
        )

    if not prediksi["pembagian"].isin(
        ["Training", "Testing"]
    ).all():
        raise ValueError("Pembagian data tidak valid.")

    if not prediksi["kelas"].isin(KELAS).all():
        raise ValueError("Label acuan tidak sesuai enam kelas.")

    if not prediksi["kelas_prediksi"].isin(KELAS).all():
        raise ValueError(
            "Prediksi tidak sesuai enam kelas."
        )

    training = prediksi[
        prediksi["pembagian"] == "Training"
    ].copy()

    testing = prediksi[
        prediksi["pembagian"] == "Testing"
    ].copy()

    if not len(testing):
        raise ValueError("Data testing kosong.")

    if len(training) != int(
        evaluasi["jumlah_training_polygon"]
    ):
        raise ValueError("Jumlah training tidak cocok.")

    if len(testing) != int(
        evaluasi["jumlah_testing_polygon"]
    ):
        raise ValueError("Jumlah testing tidak cocok.")

    benar = int(
        (
            testing["kelas"]
            == testing["kelas_prediksi"]
        ).sum()
    )

    akurasi = benar / len(testing)

    if abs(
        akurasi
        - float(evaluasi["testing_polygon"]["accuracy"])
    ) > 1e-6:
        raise ValueError("Accuracy testing tidak cocok.")

    ids_geo = [
        str(feature["properties"]["sample_id"])
        for feature in geo["features"]
    ]

    if (
        len(ids_geo) != len(set(ids_geo))
        or set(ids_geo) != set(prediksi["sample_id"])
    ):
        raise ValueError(
            "ID peta dan hasil prediksi tidak cocok."
        )

    lookup = prediksi.set_index("sample_id")

    for feature in geo["features"]:
        properties = feature["properties"]
        row = lookup.loc[str(properties["sample_id"])]

        for kolom in ["kelas", "kelas_prediksi", "pembagian"]:
            if properties[kolom] != row[kolom]:
                raise ValueError(
                    "Isi peta dan hasil prediksi tidak cocok."
                )

except Exception as error:
    st.error(f"Data tidak dapat dibaca: {error}")
    st.stop()


with st.sidebar:
    st.subheader("Filter Peta")

    kelas_dipilih = st.multiselect(
        "Pilih Kelas Tutupan Lahan:",
        options=KELAS,
        default=KELAS,
    )

    st.caption(
        "Filter berlaku pada kelas prediksi "
        "di tab Peta Spasial."
    )


tab1, tab2, tab3, tab4 = st.tabs([
    "Eksplorasi Data",
    "Peta Spasial",
    "Model Extra Trees",
    "Prediksi Data Baru",
])


with tab1:
    st.subheader("Distribusi Jumlah Sampel per Kelas")

    jumlah_polygon = (
        prediksi["kelas"]
        .value_counts()
        .reindex(KELAS, fill_value=0)
    )

    distribusi = pd.DataFrame({
        "Kelas": KELAS,
        "Jumlah Sampel": jumlah_polygon.to_numpy(),
    })

    kiri, kanan = st.columns([1, 2])

    with kiri:
        tampilkan_tabel(distribusi)
        st.write(f"Total: **{len(prediksi)} polygon sampel**.")

    with kanan:
        st.bar_chart(
            distribusi.set_index("Kelas"),
            color="#2e7d32",
        )

    st.subheader("Ringkasan Dataset")

    kolom1, kolom2, kolom3 = st.columns(3)

    kolom1.metric("Jumlah polygon", len(prediksi))
    kolom2.metric("Jumlah piksel", len(data))
    kolom3.metric("Jumlah fitur", len(fitur))

    st.write(
        "Dataset model terdiri dari baris piksel. "
        "Setiap piksel memiliki sample_id yang menghubungkannya "
        "dengan polygon sampel."
    )

    st.subheader("Cuplikan Dataset Piksel")

    tampilkan_tabel(
        data[["sample_id", "kelas"] + fitur].head(10)
    )

    st.subheader("Missing Value pada Fitur")

    missing = data[fitur].isna().sum()

    tampilkan_tabel(
        missing.rename("Jumlah Missing")
        .rename_axis("Fitur")
        .reset_index()
    )

    with st.expander("Statistik Deskriptif Fitur"):
        tampilkan_tabel(
            data[fitur]
            .describe()
            .transpose()
            .reset_index()
            .rename(columns={"index": "Fitur"})
        )

    with st.expander("Rata-rata Fitur per Kelas"):
        tampilkan_tabel(
            data.groupby("kelas")[fitur]
            .mean()
            .reindex(KELAS)
            .reset_index()
        )


with tab2:
    st.subheader("Peta Hasil Klasifikasi Lahan")

    features = [
        feature
        for feature in geo["features"]
        if feature["properties"]["kelas_prediksi"]
        in kelas_dipilih
    ]

    if not features:
        st.info(
            "Pilih minimal satu kelas di sidebar "
            "untuk menampilkan peta."
        )
    else:
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

        st.caption(
            f"Ditampilkan: {len(features)} polygon. "
            "Warna menunjukkan kelas prediksi. "
            "Penanda oranye menunjukkan kesalahan testing."
        )

        st.caption(
            "Accuracy pada legenda berasal dari seluruh "
            "36 polygon testing. Filter sidebar mengatur "
            "polygon yang ditampilkan."
        )

    st.write(
        "Pilih Google Hybrid untuk latar satelit Google "
        "dengan label. Perbesar peta lalu klik polygon "
        "atau penanda untuk melihat informasi sampel."
    )


with tab3:
    st.subheader("Model Terpilih dan Evaluasi")

    st.write(
        f"Model: **{nama_model}**. "
        "Model telah dilatih melalui klasifikasi_sentinel.py "
        "dan dimuat dari model_terbaik.joblib."
    )

    st.subheader("Pembagian Training dan Testing")

    pembagian = pd.DataFrame({
        "Total": prediksi["kelas"].value_counts(),
        "Training": training["kelas"].value_counts(),
        "Testing": testing["kelas"].value_counts(),
    }).reindex(KELAS).fillna(0).astype(int)

    tampilkan_tabel(
        pembagian.rename_axis("Kelas").reset_index()
    )

    st.write(
        "Pembagian dilakukan berdasarkan polygon: "
        "**80% training dan 20% testing**. "
        "Seluruh piksel satu polygon masuk ke kelompok "
        "yang sama."
    )

    kolom1, kolom2 = st.columns(2)

    kolom1.metric(
        "Piksel training",
        int(evaluasi["jumlah_training_piksel"]),
    )

    kolom2.metric(
        "Piksel testing",
        int(evaluasi["jumlah_testing_piksel"]),
    )

    st.subheader("Perbandingan Model")

    tabel_model = pd.DataFrame([
        {
            "Model": row["model"],
            "CV Accuracy Polygon": (
                f"{float(row['cv_accuracy_polygon']):.2%}"
            ),
            "CV Macro F1 Polygon": (
                f"{float(row['cv_macro_f1_polygon']):.6f}"
            ),
            "CV Accuracy Piksel": (
                f"{float(row['cv_accuracy_piksel']):.2%}"
            ),
        }
        for _, row in perbandingan.iterrows()
    ])

    tampilkan_tabel(tabel_model)

    st.write(
        "Perbandingan menggunakan validasi silang "
        "tiga fold pada data training. Extra Trees dan "
        "Random Forest memiliki rata-rata accuracy polygon "
        "yang sama. Extra Trees dipilih karena macro F1 "
        "polygon sedikit lebih tinggi."
    )

    st.subheader("Evaluasi Polygon Testing")

    kolom1, kolom2, kolom3 = st.columns(3)

    kolom1.metric("Accuracy", f"{akurasi:.2%}")

    kolom2.metric(
        "Macro F1",
        f"{float(evaluasi['testing_polygon']['macro_f1']):.4f}",
    )

    kolom3.metric(
        "Prediksi benar",
        f"{benar}/{len(testing)}",
    )

    tampilkan_gambar(
        "confusion_matrix_polygon.png",
        "Confusion matrix polygon testing",
    )

    st.caption(
        "Baris menunjukkan kelas acuan. "
        "Kolom menunjukkan kelas prediksi."
    )

    st.subheader("Evaluasi Piksel Testing")

    piksel = evaluasi["testing_piksel"]

    kolom1, kolom2, kolom3 = st.columns(3)

    kolom1.metric(
        "Accuracy piksel",
        f"{float(piksel['accuracy']):.2%}",
    )

    kolom2.metric(
        "Balanced accuracy",
        f"{float(piksel['balanced_accuracy']):.2%}",
    )

    kolom3.metric(
        "Macro F1 piksel",
        f"{float(piksel['macro_f1']):.4f}",
    )

    tampilkan_gambar(
        "confusion_matrix_piksel.png",
        "Confusion matrix piksel testing",
    )

    with st.expander("Lihat Prediksi Polygon Testing"):
        tampilkan_tabel(
            testing[[
                "sample_id",
                "kelas",
                "kelas_prediksi",
                "probabilitas",
                "kesesuaian",
            ]]
        )


with tab4:
    st.subheader("Prediksi Lahan dari Nilai Citra Baru")

    st.write(
        "Masukkan nilai reflektansi 10 band Sentinel-2A. "
        "NDVI, NDWI, dan NDBI dihitung otomatis "
        "untuk melengkapi 13 fitur model."
    )

    st.caption(
        "Nilai awal merupakan median fitur dataset "
        "sebagai contoh pengisian. Ganti dengan "
        "nilai reflektansi citra yang ingin diprediksi."
    )

    nilai_input = {}

    with st.form("form_prediksi"):
        kolom = st.columns(3)

        for nomor, band in enumerate(BAND):
            with kolom[nomor % 3]:
                nilai_input[band] = st.number_input(
                    LABEL_BAND[band],
                    value=float(data[band].median()),
                    step=0.001,
                    format="%.6f",
                    key=f"input_{band}",
                )

        kirim = st.form_submit_button(
            "Prediksi Kelas Lahan"
        )

    if kirim:
        try:
            nilai = dict(nilai_input)

            nilai["NDVI"] = normalized_difference(
                nilai["B08"], nilai["B04"]
            )

            nilai["NDWI"] = normalized_difference(
                nilai["B03"], nilai["B08"]
            )

            nilai["NDBI"] = normalized_difference(
                nilai["B11"], nilai["B08"]
            )

            data_baru = pd.DataFrame([nilai])[fitur]

            if not np.isfinite(
                data_baru.to_numpy(dtype=float)
            ).all():
                raise ValueError("Nilai fitur tidak valid.")

            probabilitas = model.predict_proba(
                data_baru
            )[0]

            posisi = int(np.argmax(probabilitas))
            kelas_hasil = str(model.classes_[posisi])

            st.success(
                f"Hasil prediksi: {kelas_hasil}"
            )

            st.metric(
                "Probabilitas model untuk kelas terpilih",
                f"{float(probabilitas[posisi]):.2%}",
            )

            tabel_probabilitas = pd.DataFrame({
                "Kelas": model.classes_,
                "Probabilitas": probabilitas,
            }).sort_values(
                "Probabilitas",
                ascending=False,
            )

            tabel_probabilitas["Probabilitas"] = (
                tabel_probabilitas["Probabilitas"]
                .map(lambda nilai: f"{nilai:.2%}")
            )

            tampilkan_tabel(tabel_probabilitas)

            with st.expander(
                "Lihat Input Lengkap: Band dan Indeks"
            ):
                tampilkan_tabel(data_baru)

            st.caption(
                "Prediksi ini berlaku untuk satu piksel. "
                "Prediksi polygon pada peta menggunakan "
                "rata-rata probabilitas piksel sampelnya."
            )

        except Exception as error:
            st.error(f"Prediksi gagal: {error}")