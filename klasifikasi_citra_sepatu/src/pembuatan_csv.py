"""
Script Penggabungan Fitur dan Pembuatan CSV Utama (Tahap 6)
Proyek PCD: Klasifikasi Citra Sepatu Rapi dan Berantakan
"""

import os
import sys
import json
import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) # Folder: Klasifikasi_Citra_Sepatu
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

CSV_RGB_PATH = os.path.join(OUTPUT_DIR, "fitur_rgb_sementara.csv")
CSV_GLCM_PATH = os.path.join(OUTPUT_DIR, "fitur_glcm_sementara.csv")
META_RGB_PATH = os.path.join(OUTPUT_DIR, "laporan_duplikasi_dataset.json")
META_GLCM_PATH = os.path.join(OUTPUT_DIR, "metadata_glcm.json")
FINAL_CSV_PATH = os.path.join(OUTPUT_DIR, "dataset_fitur_citra.csv")

EXPECTED_COLUMNS = [
    'mean_R', 'mean_G', 'mean_B',
    'std_R', 'std_G', 'std_B',
    'skew_R', 'skew_G', 'skew_B',
    'energy', 'entropy', 'contrast', 'correlation', 'homogeneity',
    'label'
]

def validate_and_merge():
    print("[1/5] Memeriksa keberadaan file sumber...")
    for p, name in [
        (CSV_RGB_PATH, "CSV Fitur RGB"),
        (CSV_GLCM_PATH, "CSV Fitur GLCM"),
        (META_RGB_PATH, "Metadata Tahap 3 (RGB)"),
        (META_GLCM_PATH, "Metadata Tahap 5 (GLCM)")
    ]:
        if not os.path.isfile(p):
            raise FileNotFoundError(f"[ERROR] File {name} tidak ditemukan di: {p}")
    print("      Semua file sumber ditemukan.")

    print("\n[2/5] Membaca data dan metadata...")
    df_rgb = pd.read_csv(CSV_RGB_PATH)
    df_glcm = pd.read_csv(CSV_GLCM_PATH)

    with open(META_RGB_PATH, "r", encoding="utf-8") as f:
        meta_rgb_data = json.load(f)
        meta_rgb = meta_rgb_data.get("metadata_file", [])

    with open(META_GLCM_PATH, "r", encoding="utf-8") as f:
        meta_glcm_data = json.load(f)
        meta_glcm = meta_glcm_data.get("items", [])

    print(f"      Baris CSV RGB  : {len(df_rgb)}")
    print(f"      Baris CSV GLCM : {len(df_glcm)}")
    print(f"      Metadata RGB   : {len(meta_rgb)}")
    print(f"      Metadata GLCM  : {len(meta_glcm)}")

    print("\n[3/5] Melakukan validasi ketat sebelum penggabungan:")
    # 1. Jumlah baris harus 200
    if len(df_rgb) != 200 or len(df_glcm) != 200:
        raise ValueError(f"[GAGAL] Jumlah baris tidak sesuai: RGB={len(df_rgb)}, GLCM={len(df_glcm)} (target: 200)")
    print("      [OK] Kedua CSV memiliki tepat 200 baris data.")

    # 2. Distribusi label masing-masing 100 rapi dan 100 berantakan
    rgb_counts = df_rgb['label'].value_counts().to_dict()
    glcm_counts = df_glcm['label'].value_counts().to_dict()
    if rgb_counts != {'rapi': 100, 'berantakan': 100} or glcm_counts != {'rapi': 100, 'berantakan': 100}:
        raise ValueError(f"[GAGAL] Distribusi label tidak tepat 100/100: RGB={rgb_counts}, GLCM={glcm_counts}")
    print("      [OK] Distribusi label kedua file tepat 100 'rapi' dan 100 'berantakan'.")

    # 3. Validasi urutan pasangan gambar berdasarkan metadata nama file & label
    mismatch_pairs = []
    for i in range(200):
        m_rgb = meta_rgb[i]
        m_glcm = meta_glcm[i]
        
        rgb_fn = m_rgb['filename']
        glcm_orig_fn = m_glcm['original_filename']
        rgb_lbl = m_rgb['label']
        glcm_lbl = m_glcm['label']
        csv_rgb_lbl = df_rgb.loc[i, 'label']
        csv_glcm_lbl = df_glcm.loc[i, 'label']

        if not (rgb_fn == glcm_orig_fn and rgb_lbl == glcm_lbl == csv_rgb_lbl == csv_glcm_lbl):
            mismatch_pairs.append({
                'row_index': i,
                'rgb_meta': (rgb_fn, rgb_lbl),
                'glcm_meta': (glcm_orig_fn, glcm_lbl),
                'csv_rgb_label': csv_rgb_lbl,
                'csv_glcm_label': csv_glcm_lbl
            })

    if mismatch_pairs:
        raise ValueError(f"[GAGAL] Ditemukan {len(mismatch_pairs)} pasangan baris tidak cocok! Contoh: {mismatch_pairs[:3]}")
    print("      [OK] 200 pasangan gambar 100% cocok sempurna berdasarkan nama file dan label!")

    print("\n[4/5] Menggabungkan fitur RGB dan GLCM...")
    # Mengambil 9 fitur RGB (tanpa kolom label)
    rgb_features = df_rgb[['mean_R', 'mean_G', 'mean_B', 'std_R', 'std_G', 'std_B', 'skew_R', 'skew_G', 'skew_B']]
    # Mengambil 5 fitur GLCM (tanpa kolom label)
    glcm_features = df_glcm[['energy', 'entropy', 'contrast', 'correlation', 'homogeneity']]
    # Kolom label dari data yang terverifikasi
    labels = df_rgb[['label']]

    # Gabungkan secara horizontal
    df_merged = pd.concat([rgb_features, glcm_features, labels], axis=1)

    # Pastikan urutan kolom tepat 15 kolom
    df_merged = df_merged[EXPECTED_COLUMNS]

    # Simpan CSV utama
    df_merged.to_csv(FINAL_CSV_PATH, index=False)
    print(f"      CSV utama berhasil disimpan di: {FINAL_CSV_PATH}")

    print("\n[5/5] Melakukan validasi menyeluruh terhadap CSV utama yang tersimpan...")
    # Baca ulang file dari disk
    df_reloaded = pd.read_csv(FINAL_CSV_PATH)

    # Validasi dimensi
    rows, cols = df_reloaded.shape
    if rows != 200 or cols != 15:
        raise ValueError(f"[GAGAL] Dimensi CSV salah: {df_reloaded.shape}, diharapkan (200, 15)")

    # Validasi daftar kolom
    if list(df_reloaded.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"[GAGAL] Urutan atau nama kolom tidak sesuai!\nAda: {list(df_reloaded.columns)}\nHarapan: {EXPECTED_COLUMNS}")

    # Validasi nilai NaN dan Infinity
    nan_count = df_reloaded.isna().sum().sum()
    if nan_count > 0:
        raise ValueError(f"[GAGAL] Ditemukan {nan_count} nilai NaN pada CSV utama.")

    feature_cols = EXPECTED_COLUMNS[:-1]
    inf_count = np.isinf(df_reloaded[feature_cols]).sum().sum()
    if inf_count > 0:
        raise ValueError(f"[GAGAL] Ditemukan {inf_count} nilai Infinity pada fitur numerik.")

    # Validasi tipe data
    for col in feature_cols:
        if not np.issubdtype(df_reloaded[col].dtype, np.number):
            raise TypeError(f"[GAGAL] Kolom {col} bukan bertipe numerik: {df_reloaded[col].dtype}")

    print("      [OK] Dimensi tepat: 200 baris x 15 kolom.")
    print("      [OK] 14 fitur numerik (float64) + 1 kolom label (string).")
    print("      [OK] 0 missing values (NaN) dan 0 nilai Infinity.")
    print("      [OK] Distribusi label: 100 'rapi' dan 100 'berantakan'.")
    print("      [OK] Tidak ada kolom ekstra atau terduplikasi.")

    return df_reloaded

if __name__ == '__main__':
    df = validate_and_merge()
    print("\n" + "="*70)
    print("LIMA BARIS PERTAMA CSV UTAMA (dataset_fitur_citra.csv)")
    print("="*70)
    pd.set_option('display.max_columns', 16)
    pd.set_option('display.width', 1000)
    print(df.head())

    print("\n" + "="*70)
    print("STATISTIK DESKRIPTIF 14 FITUR NUMERIK (MIN, MAX, MEAN, STD)")
    print("="*70)
    feat_cols = [c for c in df.columns if c != 'label']
    stats_df = pd.DataFrame({
        'Min': df[feat_cols].min(),
        'Max': df[feat_cols].max(),
        'Mean': df[feat_cols].mean(),
        'Std': df[feat_cols].std()
    })
    print(stats_df)

