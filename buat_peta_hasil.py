import copy
import html
import json
import webbrowser
from pathlib import Path

import folium
import joblib
import numpy as np
import pandas as pd
from folium.plugins import Fullscreen


ROOT = Path(__file__).resolve().parent

GEOJSON = ROOT / "PSD_6_Kelas_Gabungan.geojson"
DATASET = ROOT / "hasil_ekstraksi" / "dataset_piksel_sentinel.csv"
HASIL = ROOT / "hasil_klasifikasi"
MODEL = HASIL / "model_terbaik.joblib"
STATIC = ROOT / "_static"

WARNA = {
    "Sawah": "#facc15",
    "Bangunan": "#ef4444",
    "Mangrove": "#9333a8",
    "Lahan Hijau": "#228b22",
    "Laut": "#1455b5",
    "Danau": "#49bfe8",
}

NAMA_KELAS = {
    "Sawah": "Sawah",
    "Bangunan": "Bangunan",
    "Mangrove": "Mangrove",
    "Lahan Hijau": "Lahan Hijau",
    "Laut": "Perairan Terbuka (Laut)",
    "Danau": "Danau",
}

FIELDS = [
    "sample_id",
    "kelas",
    "kelas_prediksi",
    "pembagian",
    "probabilitas",
    "kesesuaian",
]

ALIASES = [
    "ID sampel",
    "Label acuan",
    "Prediksi model",
    "Kelompok data",
    "Probabilitas rata-rata tertinggi",
    "Kesesuaian dengan label",
]


def koordinat(geometry):
    def telusuri(obj):
        if (
            isinstance(obj, (list, tuple))
            and len(obj) >= 2
            and isinstance(obj[0], (int, float))
            and isinstance(obj[1], (int, float))
        ):
            yield float(obj[0]), float(obj[1])
        else:
            for bagian in obj:
                yield from telusuri(bagian)

    if not geometry:
        raise RuntimeError("Ada polygon tanpa geometri.")

    if geometry["type"] not in ("Polygon", "MultiPolygon"):
        raise RuntimeError("Geometri harus Polygon atau MultiPolygon.")

    titik = list(telusuri(geometry["coordinates"]))

    if not titik:
        raise RuntimeError("Ada polygon tanpa koordinat.")

    return titik


def pusat_penanda(feature):
    titik = koordinat(feature["geometry"])

    lon = (min(p[0] for p in titik) + max(p[0] for p in titik)) / 2
    lat = (min(p[1] for p in titik) + max(p[1] for p in titik)) / 2

    return [lat, lon]


def isi_popup(feature):
    properties = feature["properties"]

    return "<br>".join(
        f"<b>{html.escape(alias)}:</b> "
        f"{html.escape(str(properties[field]))}"
        for field, alias in zip(FIELDS, ALIASES)
    )


def style_prediksi(feature):
    warna = WARNA[feature["properties"]["kelas_prediksi"]]

    return {
        "color": warna,
        "fillColor": warna,
        "weight": 2,
        "fillOpacity": 0.65,
    }


def tambah_geojson(kelompok, features, style_function):
    if not features:
        return

    folium.GeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        style_function=style_function,
        highlight_function=lambda feature: {
            "weight": 4,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=FIELDS,
            aliases=ALIASES,
            sticky=False,
        ),
        popup=folium.GeoJsonPopup(
            fields=FIELDS,
            aliases=ALIASES,
        ),
    ).add_to(kelompok)


def tambah_layer_kelas(peta, features, kelas):
    pilihan = [
        feature
        for feature in features
        if feature["properties"]["kelas_prediksi"] == kelas
    ]

    kelompok = folium.FeatureGroup(
        name=(
            f"Prediksi {NAMA_KELAS[kelas]} "
            f"({len(pilihan)} polygon)"
        ),
        show=True,
    ).add_to(peta)

    tambah_geojson(kelompok, pilihan, style_prediksi)

    # Penanda membantu menemukan polygon kecil saat zoom jauh.
    for feature in pilihan:
        properties = feature["properties"]

        folium.CircleMarker(
            location=pusat_penanda(feature),
            radius=4,
            color="white",
            weight=1,
            fill=True,
            fill_color=WARNA[kelas],
            fill_opacity=0.95,
            tooltip=html.escape(
                f"{properties['sample_id']} — "
                f"{NAMA_KELAS[kelas]} "
                f"({properties['pembagian']})"
            ),
            popup=folium.Popup(
                isi_popup(feature),
                max_width=350,
            ),
        ).add_to(kelompok)


def buat_peta(features, nama_model, benar, jumlah_testing):
    peta = folium.Map(
        location=[-7.7, 112.8],
        zoom_start=8,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )

    # Dua pilihan latar dalam satu peta.
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
        tambah_layer_kelas(peta, features, kelas)

    data_testing = [
        feature
        for feature in features
        if feature["properties"]["pembagian"] == "Testing"
    ]

    layer_testing = folium.FeatureGroup(
        name=f"Sorot Data Uji ({len(data_testing)} polygon)",
        show=False,
    ).add_to(peta)

    tambah_geojson(
        layer_testing,
        data_testing,
        lambda feature: {
            "color": "#ffffff",
            "weight": 4,
            "fill": False,
            "fillOpacity": 0,
            "dashArray": "5, 4",
        },
    )

    for feature in data_testing:
        folium.CircleMarker(
            location=pusat_penanda(feature),
            radius=8,
            color="#ffffff",
            weight=3,
            fill=False,
            tooltip=html.escape(
                f"Data uji: {feature['properties']['sample_id']}"
            ),
            popup=folium.Popup(
                isi_popup(feature),
                max_width=350,
            ),
        ).add_to(layer_testing)

    salah_testing = [
        feature
        for feature in data_testing
        if (
            feature["properties"]["kelas"]
            != feature["properties"]["kelas_prediksi"]
        )
    ]

    layer_salah = folium.FeatureGroup(
        name=(
            "Salah Klasifikasi Testing "
            f"({len(salah_testing)} polygon)"
        ),
        show=True,
    ).add_to(peta)

    tambah_geojson(
        layer_salah,
        salah_testing,
        lambda feature: {
            "color": "#ff8c00",
            "weight": 4,
            "fill": False,
            "fillOpacity": 0,
        },
    )

    for feature in salah_testing:
        properties = feature["properties"]

        folium.Marker(
            location=pusat_penanda(feature),
            icon=folium.Icon(
                color="orange",
                icon="info-circle",
                prefix="fa",
            ),
            tooltip=html.escape(
                f"{properties['sample_id']}: "
                f"acuan {properties['kelas']} → "
                f"prediksi {properties['kelas_prediksi']}"
            ),
            popup=folium.Popup(
                isi_popup(feature),
                max_width=350,
            ),
        ).add_to(layer_salah)

    seluruh_titik = [
        titik
        for feature in features
        for titik in koordinat(feature["geometry"])
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

    layer_batas = folium.FeatureGroup(
        name="Batas sebaran sampel (bbox)",
        show=True,
    ).add_to(peta)

    folium.Rectangle(
        bounds=bounds,
        color="#ffffff",
        weight=2,
        dash_array="8, 6",
        fill=False,
        tooltip="Kotak batas sebaran seluruh sampel",
    ).add_to(layer_batas)

    peta.fit_bounds(bounds, padding=(25, 25))

    legenda_kelas = "".join(
        f"""
        <div style="margin:6px 0;display:flex;align-items:center">
            <span style="
                width:18px;
                height:18px;
                background:{warna};
                border:1px solid #555;
                margin-right:8px;
                flex-shrink:0">
            </span>
            {html.escape(NAMA_KELAS[kelas])}
        </div>
        """
        for kelas, warna in WARNA.items()
    )

    akurasi = benar / jumlah_testing

    legenda = f"""
    <div style="
        position:fixed;
        bottom:35px;
        left:15px;
        z-index:9999;
        background:white;
        color:#333;
        padding:15px 18px;
        border:1px solid #bbb;
        border-radius:8px;
        box-shadow:0 2px 10px #0004;
        font:14px Arial,sans-serif;
        max-width:275px">
        <div style="font-size:17px;font-weight:bold">
            Legenda Klasifikasi Lahan
        </div>
        <div style="font-size:12px;margin-top:5px">
            Model: {html.escape(nama_model)}
        </div>
        <hr style="border:0;border-top:1px solid #ddd">
        {legenda_kelas}
        <hr style="border:0;border-top:1px solid #ddd">
        <div style="font-size:12px;line-height:1.5">
            Warna menunjukkan kelas prediksi.<br>
            Testing: {benar}/{jumlah_testing} benar
            ({akurasi:.2%}).<br>
            Penanda oranye: salah klasifikasi testing.<br>
            Cakupan hasil: {len(features)} polygon sampel.
        </div>
    </div>
    """

    peta.get_root().html.add_child(folium.Element(legenda))

    peta.get_root().header.add_child(
        folium.Element(
            """
            <style>
                .leaflet-control-layers {
                    font:14px Arial,sans-serif;
                    border-radius:6px !important;
                    max-height:65vh;
                    overflow-y:auto;
                }
                .leaflet-control-layers-expanded {
                    padding:12px !important;
                }
                .leaflet-control-layers label {
                    margin-bottom:5px;
                }
                .leaflet-popup-content {
                    line-height:1.6;
                }
            </style>
            """
        )
    )

    Fullscreen(
        position="topleft",
        title="Layar penuh",
        title_cancel="Keluar layar penuh",
    ).add_to(peta)

    folium.LayerControl(
        collapsed=False,
        position="topright",
    ).add_to(peta)

    return peta, len(salah_testing)


def main():
    for lokasi in [GEOJSON, DATASET, MODEL]:
        if not lokasi.exists():
            raise RuntimeError(f"File tidak ditemukan: {lokasi}")

    HASIL.mkdir(parents=True, exist_ok=True)
    STATIC.mkdir(parents=True, exist_ok=True)

    bundle = joblib.load(MODEL)
    model = bundle["model"]
    fitur = list(bundle["fitur"])
    nama_model = str(bundle["nama_model"])

    training_ids = {
        str(sid) for sid in bundle["training_sample_ids"]
    }
    testing_ids = {
        str(sid) for sid in bundle["testing_sample_ids"]
    }

    if not training_ids.isdisjoint(testing_ids):
        raise RuntimeError(
            "ID training dan testing bertumpang tindih."
        )

    if not testing_ids:
        raise RuntimeError("Tidak ada ID data testing.")

    data = pd.read_csv(
        DATASET,
        dtype={"sample_id": str, "kelas": str},
    )

    kolom_wajib = {"sample_id", "kelas", *fitur}

    if not kolom_wajib.issubset(data.columns):
        kurang = sorted(kolom_wajib - set(data.columns))
        raise RuntimeError(f"Kolom dataset tidak lengkap: {kurang}")

    if data[["sample_id", "kelas"] + fitur].isna().any().any():
        raise RuntimeError("Dataset memiliki missing value.")

    if not np.isfinite(data[fitur].to_numpy(dtype=float)).all():
        raise RuntimeError("Nilai fitur tidak valid.")

    if (data.groupby("sample_id")["kelas"].nunique() != 1).any():
        raise RuntimeError(
            "Satu sample_id memiliki beberapa label."
        )

    if set(data["sample_id"]) != (training_ids | testing_ids):
        raise RuntimeError(
            "ID dataset berbeda dari pembagian model."
        )

    kelas_model = [str(kelas) for kelas in model.classes_]

    if set(kelas_model) != set(WARNA):
        raise RuntimeError(
            f"Kelas model tidak sesuai enam kelas: {kelas_model}"
        )

    print("Menghitung prediksi polygon...")

    probabilitas = pd.DataFrame(
        model.predict_proba(data[fitur]),
        columns=kelas_model,
    )

    probabilitas.insert(
        0,
        "sample_id",
        data["sample_id"].to_numpy(),
    )

    rata = probabilitas.groupby("sample_id").mean()
    acuan = data.groupby("sample_id")["kelas"].first()

    prediksi = pd.DataFrame({
        "sample_id": rata.index,
        "kelas": acuan.reindex(rata.index).to_numpy(),
        "kelas_prediksi": rata.idxmax(axis=1).to_numpy(),
        "probabilitas_model": rata.max(axis=1).to_numpy(),
    })

    prediksi["pembagian"] = prediksi["sample_id"].map(
        lambda sid: "Testing" if sid in testing_ids else "Training"
    )

    prediksi["probabilitas"] = prediksi[
        "probabilitas_model"
    ].map(lambda nilai: f"{nilai:.2%}")

    prediksi["kesesuaian"] = np.where(
        prediksi["kelas"] == prediksi["kelas_prediksi"],
        "Sesuai label",
        "Berbeda label",
    )

    lookup = prediksi.set_index("sample_id")

    geo = json.loads(GEOJSON.read_text(encoding="utf-8-sig"))

    ids_geo = [
        str(feature["properties"]["sample_id"])
        for feature in geo["features"]
    ]

    if len(ids_geo) != len(set(ids_geo)):
        raise RuntimeError("Ada ID GeoJSON berulang.")

    if set(ids_geo) != set(lookup.index):
        raise RuntimeError(
            "ID GeoJSON dan hasil prediksi tidak cocok."
        )

    features = []

    for feature_asli in geo["features"]:
        feature = copy.deepcopy(feature_asli)
        properties = feature["properties"]
        sid = str(properties["sample_id"])
        row = lookup.loc[sid]

        if properties["kelas"] != row["kelas"]:
            raise RuntimeError(
                f"Label GeoJSON dan dataset berbeda: {sid}"
            )

        koordinat(feature["geometry"])

        for field in FIELDS:
            properties[field] = (
                sid if field == "sample_id" else str(row[field])
            )

        features.append(feature)

    hasil_geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    lokasi_geojson = HASIL / "hasil_prediksi_polygon.geojson"

    lokasi_geojson.write_text(
        json.dumps(
            hasil_geojson,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    prediksi.to_csv(
        HASIL / "prediksi_peta_polygon.csv",
        index=False,
        encoding="utf-8-sig",
    )

    testing = prediksi[prediksi["pembagian"] == "Testing"]

    benar = int(
        (testing["kelas"] == testing["kelas_prediksi"]).sum()
    )

    print("Membuat peta Folium...")

    peta, jumlah_salah = buat_peta(
        features,
        nama_model,
        benar,
        len(testing),
    )

    lokasi_html = STATIC / "peta_klasifikasi_sentinel.html"
    peta.save(str(lokasi_html))

    print("\nPETA BERHASIL DIBUAT")
    print("Model:", nama_model)
    print("Jumlah polygon:", len(features))
    print("Training:", len(training_ids), "polygon")
    print("Testing:", len(testing), "polygon")
    print("Salah klasifikasi testing:", jumlah_salah, "polygon")
    print(f"Akurasi testing polygon: {benar / len(testing):.2%}")

    print("\nJUMLAH POLYGON BERDASARKAN PREDIKSI:")
    for kelas in WARNA:
        jumlah = int((prediksi["kelas_prediksi"] == kelas).sum())
        print(f"{NAMA_KELAS[kelas]}: {jumlah}")

    print("\nFile HTML:", lokasi_html)
    print("File GeoJSON:", lokasi_geojson)

    webbrowser.open(lokasi_html.resolve().as_uri())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("GAGAL:", error)