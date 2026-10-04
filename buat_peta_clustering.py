from pathlib import Path

import folium
import pandas as pd
from folium.plugins import Fullscreen
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


folder = Path(__file__).parent

file_input = folder / "Hasil_Clustering_Linear_PCA37_K3.csv"
file_output = folder / "Hasil_Clustering_Linear_PCA37_K3_Koordinat.csv"
file_peta = folder / "Peta_Clustering_Linear_PCA37_K3.html"


# ==================================================
# 1. MEMBACA HASIL CLUSTERING
# ==================================================

df = pd.read_csv(file_input)

kolom_wajib = {"nama", "daerah", "Cluster"}
kolom_hilang = kolom_wajib - set(df.columns)

if kolom_hilang:
    raise ValueError(
        f"Kolom tidak ditemukan: {sorted(kolom_hilang)}"
    )


# ==================================================
# 2. PENYERAGAMAN NAMA DAERAH
# ==================================================

perbaikan_daerah = {
    "Baron Nganjuk":
        "Baron, Nganjuk, Jawa Timur, Indonesia",

    "Nunukan":
        "Nunukan, Kalimantan Utara, Indonesia",

    "Sreseh, Sampang":
        "Sreseh, Sampang, Jawa Timur, Indonesia",

    "Manyar, Gresik":
        "Manyar, Gresik, Jawa Timur, Indonesia",

    "Kamal, Bangkalan":
        "Kamal, Bangkalan, Jawa Timur, Indonesia",

    "Kedungpring Lamongan":
        "Kedungpring, Lamongan, Jawa Timur, Indonesia",

    "Gresik Kota, Gresik":
        "Kecamatan Gresik, Gresik, Jawa Timur, Indonesia",

    "Waru, Pamekasan":
        "Waru, Pamekasan, Jawa Timur, Indonesia",

    "Paciran, Lamongan":
        "Paciran, Lamongan, Jawa Timur, Indonesia",

    "Kertosono, Nganjuk":
        "Kertosono, Nganjuk, Jawa Timur, Indonesia",

    "Jabon , Sidoarjo":
        "Jabon, Sidoarjo, Jawa Timur, Indonesia",

    "Menganti, Gresik":
        "Menganti, Gresik, Jawa Timur, Indonesia",

    "Widang, Tuban":
        "Widang, Tuban, Jawa Timur, Indonesia",

    "Sidoarjo, Wonoayu":
        "Wonoayu, Sidoarjo, Jawa Timur, Indonesia",

    "Kwanyar, Bangkalan":
        "Kwanyar, Bangkalan, Jawa Timur, Indonesia",

    "sambeng, lamongan":
        "Sambeng, Lamongan, Jawa Timur, Indonesia",

    "Kec. Kalianget, Sumenep":
        "Kalianget, Sumenep, Jawa Timur, Indonesia",

    "Cerme, Gresik":
        "Cerme, Gresik, Jawa Timur, Indonesia",

    "Tikala, Manado":
        "Tikala, Manado, Sulawesi Utara, Indonesia",

    "Kerek, Tuban":
        "Kerek, Tuban, Jawa Timur, Indonesia",

    "Wonokromo, Surabaya":
        "Wonokromo, Surabaya, Jawa Timur, Indonesia",

    "Asemrowo, Surabaya":
        "Asem Rowo, Surabaya, Jawa Timur, Indonesia",

    "Kota Sumenep, Sumenep":
        "Kota Sumenep, Jawa Timur, Indonesia",

    "Socah, Bangkalan":
        "Socah, Bangkalan, Jawa Timur, Indonesia",

    "Pilangkenceng, Madiun":
        "Pilangkenceng, Madiun, Jawa Timur, Indonesia",

    "Tanah Merah, Bangkalan":
        "Tanah Merah, Bangkalan, Jawa Timur, Indonesia",

    "Labang, Bangkalan":
        "Labang, Bangkalan, Jawa Timur, Indonesia",

    "Widodaren, Ngawi":
        "Widodaren, Ngawi, Jawa Timur, Indonesia",

    "Bangkalan, Bangkalan":
        "Kecamatan Bangkalan, Jawa Timur, Indonesia",

    "Warudoyong, Kota Sukabumi":
        "Warudoyong, Sukabumi, Jawa Barat, Indonesia",

    "Dukun, Gresik":
        "Dukun, Gresik, Jawa Timur, Indonesia",

    "Kecamatan Bangkalan,Bangkalan":
        "Kecamatan Bangkalan, Jawa Timur, Indonesia",
}


# Koordinat manual untuk daerah yang tidak ditemukan geocoder
koordinat_manual = {
    "Banyu Ajuh, Perumnas, Kamal": (
        -7.1702821,
        112.7288563,
    ),

    "Bandung - Jogoroto, Jombang": (
        -7.5385000,
        112.3520000,
    ),

    "Banyuajuh kamal, Bangkalan": (
        -7.1702821,
        112.7288563,
    ),
}


# ==================================================
# 3. MENCARI KOORDINAT
# ==================================================

geolocator = Nominatim(
    user_agent="peta_cluster_psd_riska_2026",
    timeout=20,
)

geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    swallow_exceptions=True,
)

cache = {}


def cari_koordinat(daerah):
    daerah_asli = str(daerah).strip()

    # Gunakan koordinat manual terlebih dahulu
    if daerah_asli in koordinat_manual:
        latitude, longitude = koordinat_manual[daerah_asli]

        print(
            f"Koordinat manual: {daerah_asli} "
            f"({latitude}, {longitude})"
        )

        return (
            latitude,
            longitude,
            "Koordinat manual",
        )

    query = perbaikan_daerah.get(
        daerah_asli,
        f"{daerah_asli}, Indonesia",
    )

    if query in cache:
        return cache[query]

    print(f"Mencari: {query}")

    lokasi = geocode(query)

    if lokasi is None:
        print(f"  Gagal ditemukan: {daerah_asli}")

        hasil = (
            None,
            None,
            query,
        )
    else:
        print(
            f"  Ditemukan: "
            f"{lokasi.latitude}, {lokasi.longitude}"
        )

        hasil = (
            lokasi.latitude,
            lokasi.longitude,
            query,
        )

    cache[query] = hasil

    return hasil


hasil = df["daerah"].apply(cari_koordinat)

df["latitude"] = hasil.apply(
    lambda nilai: nilai[0]
)

df["longitude"] = hasil.apply(
    lambda nilai: nilai[1]
)

df["query_geocoding"] = hasil.apply(
    lambda nilai: nilai[2]
)


# ==================================================
# 4. MEMERIKSA HASIL KOORDINAT
# ==================================================

df_valid = df.dropna(
    subset=["latitude", "longitude"]
).copy()

df_gagal = df[
    df[["latitude", "longitude"]]
    .isna()
    .any(axis=1)
].copy()

df.to_csv(
    file_output,
    index=False,
)


print("\nRingkasan geocoding")
print("Total data:", len(df))
print("Berhasil:", len(df_valid))
print("Gagal:", len(df_gagal))

if not df_gagal.empty:
    print("\nDaerah yang gagal ditemukan:")

    print(
        df_gagal[
            ["nama", "daerah"]
        ].to_string(index=False)
    )


if df_valid.empty:
    raise ValueError(
        "Tidak ada koordinat yang berhasil ditemukan."
    )


# ==================================================
# 5. MEMBUAT PETA INTERAKTIF
# ==================================================

pusat_peta = [
    df_valid["latitude"].mean(),
    df_valid["longitude"].mean(),
]

peta = folium.Map(
    location=pusat_peta,
    zoom_start=7,
    tiles=None,
    control_scale=True,
)


# Peta dasar Google Satellite
folium.TileLayer(
    tiles=(
        "https://mt1.google.com/vt/"
        "lyrs=y&x={x}&y={y}&z={z}"
    ),
    attr="Google Satellite",
    name="Google Satellite",
    overlay=False,
    control=True,
    show=True,
).add_to(peta)


# Peta dasar OpenStreetMap
folium.TileLayer(
    tiles="OpenStreetMap",
    name="OpenStreetMap",
    overlay=False,
    control=True,
    show=False,
).add_to(peta)


warna_cluster = {
    "cluster_0": "#ff0000",
    "cluster_1": "#0088ff",
    "cluster_2": "#00cc44",
}


# Membuat layer untuk setiap cluster
layer_cluster = {}

for cluster in sorted(df_valid["Cluster"].unique()):
    layer = folium.FeatureGroup(
        name=cluster,
        show=True,
    )

    layer.add_to(peta)
    layer_cluster[cluster] = layer


# Menambahkan titik hasil clustering
for _, baris in df_valid.iterrows():
    cluster = str(baris["Cluster"])

    warna = warna_cluster.get(
        cluster,
        "#984ea3",
    )

    isi_popup = f"""
    <div style="width:270px">
        <h4>Hasil Clustering</h4>
        <b>Nama:</b> {baris['nama']}<br>
        <b>Daerah:</b> {baris['daerah']}<br>
        <b>Cluster:</b> {cluster}<br>
        <b>Interpolasi:</b> Linear<br>
        <b>Reduksi:</b> PCA 37<br>
        <b>Jumlah cluster:</b> k = 3
    </div>
    """

    folium.CircleMarker(
        location=[
            baris["latitude"],
            baris["longitude"],
        ],
        radius=9,
        color="#ffffff",
        weight=2,
        fill=True,
        fill_color=warna,
        fill_opacity=0.90,
        tooltip=(
            f"{baris['nama']} - {cluster}"
        ),
        popup=folium.Popup(
            isi_popup,
            max_width=330,
        ),
    ).add_to(
        layer_cluster[cluster]
    )


# ==================================================
# 6. JUDUL DAN LEGENDA
# ==================================================

judul = """
<div style="
    position: fixed;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    background-color: white;
    padding: 10px 18px;
    border: 2px solid #444;
    border-radius: 7px;
    font-size: 17px;
    font-weight: bold;
    text-align: center;
">
Peta Hasil Clustering Linear PCA 37
<br>
<span style="font-size:13px;">
K-Means k = 3
</span>
</div>
"""

peta.get_root().html.add_child(
    folium.Element(judul)
)


legenda = """
<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    z-index: 9999;
    background-color: white;
    padding: 12px 16px;
    border: 2px solid #555;
    border-radius: 7px;
    font-size: 14px;
">
<b>Legenda Cluster</b><br>
<span style="color:#ff0000;font-size:20px;">●</span>
Cluster 0<br>
<span style="color:#0088ff;font-size:20px;">●</span>
Cluster 1<br>
<span style="color:#00cc44;font-size:20px;">●</span>
Cluster 2
</div>
"""

peta.get_root().html.add_child(
    folium.Element(legenda)
)


# ==================================================
# 7. MENYESUAIKAN BATAS PETA
# ==================================================

batas_peta = [
    [
        df_valid["latitude"].min(),
        df_valid["longitude"].min(),
    ],
    [
        df_valid["latitude"].max(),
        df_valid["longitude"].max(),
    ],
]

peta.fit_bounds(
    batas_peta,
    padding=(30, 30),
)


Fullscreen(
    position="topright"
).add_to(peta)

folium.LayerControl(
    collapsed=False
).add_to(peta)


# ==================================================
# 8. MENYIMPAN PETA
# ==================================================

peta.save(file_peta)

print("\nPeta clustering berhasil dibuat.")
print("CSV koordinat:", file_output)
print("Peta HTML:", file_peta)