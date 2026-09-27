import os
from pathlib import Path
from urllib.parse import quote_plus

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine


folder_materi = Path(__file__).parent

input_file = (
    folder_materi
    / "AsemRowo_TSFEL_204_Windowed.csv"
)

output_normalisasi = (
    folder_materi
    / "AsemRowo_TSFEL_204_Normalized.csv"
)

output_pca = (
    folder_materi
    / "AsemRowo_PCA_37.csv"
)

output_evaluasi = (
    folder_materi
    / "AsemRowo_Evaluasi_Cluster.csv"
)

output_hasil_pca = (
    folder_materi
    / "AsemRowo_PCA37_Clustered.csv"
)

output_hasil_204 = (
    folder_materi
    / "AsemRowo_204Fitur_Clustered.csv"
)

output_variance = (
    folder_materi
    / "AsemRowo_PCA_Explained_Variance.csv"
)

folder_gambar = folder_materi / "_static"
folder_gambar.mkdir(exist_ok=True)


# ============================================================
# MEMBACA DATA
# ============================================================

if not input_file.exists():
    raise FileNotFoundError(
        f"File tidak ditemukan: {input_file}"
    )

df = pd.read_csv(input_file)

if df.shape != (49, 204):
    print(
        "Peringatan: ukuran data bukan (49, 204), "
        f"tetapi {df.shape}."
    )

df = df.replace(
    [np.inf, -np.inf],
    np.nan,
)

if df.isna().any().any():
    raise ValueError(
        "Data masih memiliki missing value atau infinity."
    )

if not all(
    pd.api.types.is_numeric_dtype(df[kolom])
    for kolom in df.columns
):
    raise ValueError(
        "Semua kolom harus berupa data numerik."
    )


# ============================================================
# MENGHAPUS FITUR KONSTAN
# ============================================================

variansi = df.var()

kolom_nonkonstan = variansi[
    variansi > 0
].index.tolist()

kolom_konstan = variansi[
    variansi <= 0
].index.tolist()

df_nonkonstan = df[
    kolom_nonkonstan
].copy()

print("Ukuran data awal:", df.shape)
print("Jumlah fitur konstan:", len(kolom_konstan))
print(
    "Jumlah fitur setelah Low Variance Filter:",
    df_nonkonstan.shape[1],
)

if df_nonkonstan.shape[1] < 37:
    raise ValueError(
        "Jumlah fitur nonkonstan kurang dari 37."
    )


# ============================================================
# NORMALISASI
# ============================================================

scaler = StandardScaler()

data_normal = scaler.fit_transform(
    df_nonkonstan
)

df_normal = pd.DataFrame(
    data_normal,
    columns=df_nonkonstan.columns,
)

df_normal.to_csv(
    output_normalisasi,
    index=False,
)


# ============================================================
# PCA MENJADI 37 KOMPONEN
# ============================================================

pca = PCA(
    n_components=37,
)

data_pca = pca.fit_transform(
    data_normal
)

nama_pca = [
    f"PCA_{nomor}"
    for nomor in range(1, 38)
]

df_pca = pd.DataFrame(
    data_pca,
    columns=nama_pca,
)

df_pca.to_csv(
    output_pca,
    index=False,
)


# Explained variance
df_variance = pd.DataFrame(
    {
        "komponen": nama_pca,
        "explained_variance_ratio": (
            pca.explained_variance_ratio_
        ),
        "cumulative_explained_variance": (
            np.cumsum(
                pca.explained_variance_ratio_
            )
        ),
    }
)

df_variance.to_csv(
    output_variance,
    index=False,
)


# ============================================================
# EVALUASI JUMLAH CLUSTER
# ============================================================

hasil_evaluasi = []

model_terbaik_pca = None
model_terbaik_204 = None

silhouette_terbaik_pca = -1
silhouette_terbaik_204 = -1

k_terbaik_pca = None
k_terbaik_204 = None


for k in range(2, 11):
    # K-Means pada PCA 37
    model_pca = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20,
    )

    label_pca = model_pca.fit_predict(
        data_pca
    )

    silhouette_pca = silhouette_score(
        data_pca,
        label_pca,
    )

    inertia_pca = model_pca.inertia_

    # K-Means pada fitur hasil normalisasi
    model_204 = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20,
    )

    label_204 = model_204.fit_predict(
        data_normal
    )

    silhouette_204 = silhouette_score(
        data_normal,
        label_204,
    )

    inertia_204 = model_204.inertia_

    hasil_evaluasi.append(
        {
            "jumlah_cluster": k,
            "inertia_pca37": inertia_pca,
            "silhouette_pca37": silhouette_pca,
            "inertia_204_fitur": inertia_204,
            "silhouette_204_fitur": silhouette_204,
        }
    )

    if silhouette_pca > silhouette_terbaik_pca:
        silhouette_terbaik_pca = silhouette_pca
        k_terbaik_pca = k
        model_terbaik_pca = model_pca

    if silhouette_204 > silhouette_terbaik_204:
        silhouette_terbaik_204 = silhouette_204
        k_terbaik_204 = k
        model_terbaik_204 = model_204


df_evaluasi = pd.DataFrame(
    hasil_evaluasi
)

df_evaluasi.to_csv(
    output_evaluasi,
    index=False,
)


# ============================================================
# MENYIMPAN LABEL CLUSTER TERBAIK
# ============================================================

df_hasil_pca = df_pca.copy()

df_hasil_pca["cluster"] = (
    model_terbaik_pca.labels_
)

df_hasil_pca.to_csv(
    output_hasil_pca,
    index=False,
)


df_hasil_204 = df_normal.copy()

df_hasil_204["cluster"] = (
    model_terbaik_204.labels_
)

df_hasil_204.to_csv(
    output_hasil_204,
    index=False,
)


# ============================================================
# MEMBUAT GRAFIK ELBOW
# ============================================================

plt.figure(
    figsize=(9, 5),
    dpi=200,
)

plt.plot(
    df_evaluasi["jumlah_cluster"],
    df_evaluasi["inertia_pca37"],
    marker="o",
    label="PCA 37",
)

plt.plot(
    df_evaluasi["jumlah_cluster"],
    df_evaluasi["inertia_204_fitur"],
    marker="o",
    label="204 fitur",
)

plt.xlabel("Jumlah Cluster (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method K-Means")
plt.xticks(range(2, 11))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    folder_gambar
    / "elbow_pca37_dan_204.png",
    bbox_inches="tight",
)

plt.close()


# ============================================================
# GRAFIK SILHOUETTE
# ============================================================

plt.figure(
    figsize=(9, 5),
    dpi=200,
)

plt.plot(
    df_evaluasi["jumlah_cluster"],
    df_evaluasi["silhouette_pca37"],
    marker="o",
    label="PCA 37",
)

plt.plot(
    df_evaluasi["jumlah_cluster"],
    df_evaluasi["silhouette_204_fitur"],
    marker="o",
    label="204 fitur",
)

plt.xlabel("Jumlah Cluster (k)")
plt.ylabel("Silhouette Score")
plt.title("Evaluasi Silhouette Score")
plt.xticks(range(2, 11))
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    folder_gambar
    / "silhouette_pca37_dan_204.png",
    bbox_inches="tight",
)

plt.close()


# ============================================================
# SCATTER PLOT CLUSTER PCA
# ============================================================

plt.figure(
    figsize=(8, 6),
    dpi=200,
)

scatter = plt.scatter(
    df_hasil_pca["PCA_1"],
    df_hasil_pca["PCA_2"],
    c=df_hasil_pca["cluster"],
    cmap="viridis",
    s=55,
)

plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.title(
    f"K-Means PCA 37 "
    f"(k={k_terbaik_pca})"
)

plt.grid(alpha=0.25)
plt.colorbar(
    scatter,
    label="Cluster",
)
plt.tight_layout()

plt.savefig(
    folder_gambar
    / "cluster_pca37.png",
    bbox_inches="tight",
)

plt.close()


# ============================================================
# UPLOAD HASIL KE AIVEN
# ============================================================

load_dotenv(
    folder_materi / ".env"
)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all(
    [
        DB_HOST,
        DB_PORT,
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
    ]
):
    raise ValueError(
        "Konfigurasi Aiven di .env belum lengkap."
    )

password_encoded = quote_plus(
    DB_PASSWORD
)

uri = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{password_encoded}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode=require"
)

engine = create_engine(
    uri,
    pool_pre_ping=True,
)

tabel_upload = {
    "asemrowo_tsfel_204_normalized": (
        df_normal
    ),
    "asemrowo_pca_37": (
        df_pca
    ),
    "asemrowo_evaluasi_cluster": (
        df_evaluasi
    ),
    "asemrowo_pca37_clustered": (
        df_hasil_pca
    ),
    "asemrowo_204fitur_clustered": (
        df_hasil_204
    ),
    "asemrowo_pca_explained_variance": (
        df_variance
    ),
}

for nama_tabel, data_tabel in tabel_upload.items():
    data_tabel.to_sql(
        nama_tabel,
        engine,
        schema="public",
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=10,
    )

    print(
        f"{nama_tabel} berhasil diunggah: "
        f"{data_tabel.shape}"
    )

engine.dispose()


# ============================================================
# LAPORAN AKHIR
# ============================================================

print("\nAnalisis data Tugas 5 berhasil.")
print("Ukuran data normal:", df_normal.shape)
print("Ukuran PCA:", df_pca.shape)

print(
    "Total explained variance PCA 37:",
    round(
        df_variance[
            "explained_variance_ratio"
        ].sum(),
        6,
    ),
)

print(
    "Cluster terbaik PCA 37:",
    k_terbaik_pca,
)

print(
    "Silhouette terbaik PCA 37:",
    round(
        silhouette_terbaik_pca,
        6,
    ),
)

print(
    "Cluster terbaik 204 fitur:",
    k_terbaik_204,
)

print(
    "Silhouette terbaik 204 fitur:",
    round(
        silhouette_terbaik_204,
        6,
    ),
)

print("\nFile hasil tersimpan:")
print(output_normalisasi)
print(output_pca)
print(output_variance)
print(output_evaluasi)
print(output_hasil_pca)
print(output_hasil_204)

print(
    "\nSeluruh data Tugas 5 sudah siap "
    "digunakan di KNIME dan web statis."
)