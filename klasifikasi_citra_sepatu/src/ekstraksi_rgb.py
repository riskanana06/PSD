"""
Script Ekstraksi Fitur Statistik RGB (Tahap 3)
Proyek PCD: Klasifikasi Citra Sepatu Rapi dan Berantakan
"""

import os
import sys
import json
import hashlib
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.stats import skew
from PIL import Image
import pillow_heif

# Registrasi heif opener agar PIL dapat membaca .heic
pillow_heif.register_heif_opener()

# A. Lokasi dataset dan output relatif terhadap lokasi file script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) # Folder: klasifikasi_citra_sepatu
PARENT_DIR = os.path.dirname(PROJECT_DIR)  # Folder: PSD (atau psd new)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def resolve_dataset_dir(subpath):
    candidates = [
        os.path.join(PARENT_DIR, subpath),
        os.path.join(PARENT_DIR, "PSD", subpath),
        os.path.join(os.path.dirname(PARENT_DIR), "PSD", subpath),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return candidates[0]

DATASET_PATHS = {
    'rapi': resolve_dataset_dir(os.path.join("rapi-20261112T014224Z-1-001", "rapi")),
    'berantakan': resolve_dataset_dir(os.path.join("berantakan-20261112T020312Z-1-001", "berantakan"))
}

def validate_dataset_paths():
    """Memvalidasi keberadaan kedua direktori dataset sebelum proses dimulai."""
    for label, folder_path in DATASET_PATHS.items():
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"[ERROR] Folder dataset '{label}' TIDAK ditemukan di: {folder_path}")
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"[ERROR] Path dataset '{label}' bukan direktori: {folder_path}")
    print("[VALIDASI PATH] Kedua folder dataset berhasil ditemukan:")
    for label, folder_path in DATASET_PATHS.items():
        print(f"  - {label.upper():10s}: {folder_path}")

def compute_file_md5(file_path):
    """Menghitung MD5 checksum untuk deteksi file biner identik."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def compute_dhash(image, hash_size=8):
    """
    Menghitung difference hash (dHash) 64-bit untuk deteksi kemiripan visual.
    Mengubah ukuran ke (hash_size + 1, hash_size), konversi ke grayscale L,
    dan membandingkan intensitas piksel kolom horizontal.
    """
    resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized)
    diff = pixels[:, 1:] > pixels[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

def hamming_distance(h1, h2):
    """Menghitung jarak Hamming antara dua nilai hash 64-bit."""
    return bin(h1 ^ h2).count('1')

def extract_rgb_features():
    # Validasi path sebelum mulai
    validate_dataset_paths()
    
    csv_rows = []
    metadata_rows = [] # untuk pencatatan nama file & duplikasi terpisah
    failed_images = []
    
    total_processed = 0
    
    for label in ['rapi', 'berantakan']:
        folder_path = DATASET_PATHS[label]
        filenames = sorted(os.listdir(folder_path))
        print(f"\n[MEMPROSES KELAS] {label.upper()} ({len(filenames)} file)...", flush=True)
        
        for idx, filename in enumerate(filenames):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue
                
            try:
                # 1. Hitung MD5 file asli
                file_md5 = compute_file_md5(file_path)
                
                # 2. Buka gambar (JPG, JPEG, HEIC)
                with Image.open(file_path) as img:
                    # 3. Konversi ke mode RGB (3 channel Red, Green, Blue)
                    rgb_img = img.convert('RGB')
                    img_array = np.array(rgb_img)
                    
                    # 4. Hitung dHash 64-bit
                    dh = compute_dhash(rgb_img)
                    
                    # 5. Pisahkan channel dengan urutan pasti:
                    # Channel 0 = Red, Channel 1 = Green, Channel 2 = Blue
                    R_ch = img_array[:, :, 0]
                    G_ch = img_array[:, :, 1]
                    B_ch = img_array[:, :, 2]
                    
                    # 6. MEAN menggunakan NumPy
                    mean_R = float(np.mean(R_ch, dtype=np.float64))
                    mean_G = float(np.mean(G_ch, dtype=np.float64))
                    mean_B = float(np.mean(B_ch, dtype=np.float64))
                    
                    # 7. STANDARD DEVIATION menggunakan NumPy dengan ddof=0
                    std_R = float(np.std(R_ch, ddof=0, dtype=np.float64))
                    std_G = float(np.std(G_ch, ddof=0, dtype=np.float64))
                    std_B = float(np.std(B_ch, ddof=0, dtype=np.float64))
                    
                    # 8. Pemeriksaan channel konstan (std == 0)
                    # Pada channel konstan, deviasi = 0 sehingga skewness tidak terdefinisi secara matematis.
                    # Jangan diganti diam-diam dengan nol; catat sebagai nilai tidak valid.
                    for ch_name, ch_std in [('Red', std_R), ('Green', std_G), ('Blue', std_B)]:
                        if ch_std == 0.0:
                            raise ValueError(f"Channel {ch_name} bersifat konstan (std = 0.0). Skewness tidak terdefinisi.")
                    
                    # 9. SKEWNESS menggunakan SciPy dengan bias=True secara konsisten
                    skew_R = float(skew(R_ch, axis=None, bias=True))
                    skew_G = float(skew(G_ch, axis=None, bias=True))
                    skew_B = float(skew(B_ch, axis=None, bias=True))
                    
                    # 10. Validasi nilai numerik valid dan finite (tidak NaN dan tidak Inf)
                    values = [mean_R, mean_G, mean_B, std_R, std_G, std_B, skew_R, skew_G, skew_B]
                    if not all(np.isfinite(v) for v in values):
                        raise ValueError(f"Nilai fitur tidak finite / mengandung NaN: {values}")
                        
                    # Row CSV utama: Tepat 10 kolom (9 fitur numerik + 1 kolom label)
                    csv_rows.append({
                        'mean_R': mean_R,
                        'mean_G': mean_G,
                        'mean_B': mean_B,
                        'std_R': std_R,
                        'std_G': std_G,
                        'std_B': std_B,
                        'skew_R': skew_R,
                        'skew_G': skew_G,
                        'skew_B': skew_B,
                        'label': label
                    })
                    
                    # Metadata disimpan terpisah (tidak masuk CSV utama)
                    metadata_rows.append({
                        'index': len(csv_rows) - 1,
                        'filename': filename,
                        'label': label,
                        'file_md5': file_md5,
                        'dhash_int': dh,
                        'dhash_hex': hex(dh)
                    })
                    
                    total_processed += 1
                    if total_processed % 20 == 0:
                        print(f"  Progress: {total_processed}/200 gambar selesai diproses...", flush=True)
                    
            except Exception as e:
                failed_images.append({
                    'label': label,
                    'filename': filename,
                    'error': str(e)
                })
                print(f"  [ERROR] {filename}: {e}", flush=True)
                
    # D. Simpan hasil CSV utama
    df_features = pd.DataFrame(csv_rows)
    csv_temp_path = os.path.join(OUTPUT_DIR, "fitur_rgb_sementara.csv")
    df_features.to_csv(csv_temp_path, index=False)
    
    # Penanganan gambar gagal jika ada
    failed_report_path = os.path.join(OUTPUT_DIR, "laporan_gambar_gagal.txt")
    if failed_images:
        with open(failed_report_path, "w", encoding="utf-8") as f:
            f.write("=== LAPORAN GAMBAR GAGAL DIPROSES ===\n\n")
            f.write(f"Total gambar gagal: {len(failed_images)}\n\n")
            for item in failed_images:
                f.write(f"- File: [{item['label']}] {item['filename']}\n")
                f.write(f"  Penyebab: {item['error']}\n\n")
    elif os.path.exists(failed_report_path):
        os.remove(failed_report_path)
        
    # C. Analisis Duplikasi: MD5 (Identik) dan dHash (Jarak Hamming)
    # 1. Kelompok MD5 (Identik Biner)
    md5_groups = defaultdict(list)
    for m in metadata_rows:
        md5_groups[m['file_md5']].append(m)
    
    duplicate_md5_list = []
    g_md5_id = 1
    for md5_val, items in md5_groups.items():
        if len(items) > 1:
            duplicate_md5_list.append({
                'group_id': f"EXACT_MD5_{g_md5_id}",
                'type': 'exact_binary_md5',
                'md5': md5_val,
                'count': len(items),
                'files': [{'label': it['label'], 'filename': it['filename']} for it in items]
            })
            g_md5_id += 1
            
    # 2. Analisis dHash dengan Jarak Hamming
    # Ambang Batas (Threshold):
    # - Hamming Distance = 0: Identik secara visual (perceptual identical, contoh: pasangan HEIC dan JPG)
    # - Hamming Distance 1 s/d 5: Sangat mirip secara visual (near-duplicate / burst shot / kompresi berbeda)
    pairwise_similar = []
    n_meta = len(metadata_rows)
    for i in range(n_meta):
        for j in range(i + 1, n_meta):
            m1 = metadata_rows[i]
            m2 = metadata_rows[j]
            dist = hamming_distance(m1['dhash_int'], m2['dhash_int'])
            if dist <= 5: # Ambang batas kemiripan visual
                pairwise_similar.append({
                    'hamming_distance': dist,
                    'file1': {'label': m1['label'], 'filename': m1['filename']},
                    'file2': {'label': m2['label'], 'filename': m2['filename']},
                    'dhash1': m1['dhash_hex'],
                    'dhash2': m2['dhash_hex'],
                    'category': 'identik_visual' if dist == 0 else 'sangat_mirip_visual'
                })

    # Simpan laporan duplikasi dalam format JSON
    json_report_path = os.path.join(OUTPUT_DIR, "laporan_duplikasi_dataset.json")
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump({
            'total_gambar_diproses': len(metadata_rows),
            'ambang_jarak_hamming': {
                'identik_visual': 'Hamming Distance = 0',
                'sangat_mirip_visual': 'Hamming Distance <= 5'
            },
            'duplikasi_md5_exact': duplicate_md5_list,
            'kemiripan_visual_dhash': pairwise_similar,
            'metadata_file': [{
                'filename': m['filename'],
                'label': m['label'],
                'md5': m['file_md5'],
                'dhash': m['dhash_hex']
            } for m in metadata_rows]
        }, f, indent=2)
        
    # Simpan laporan duplikasi dalam format TXT
    txt_report_path = os.path.join(OUTPUT_DIR, "laporan_duplikasi_dataset.txt")
    with open(txt_report_path, "w", encoding="utf-8") as f:
        f.write("====================================================================\n")
        f.write("      LAPORAN ANALISIS DUPLIKASI DAN KEMIRIPAN CITRA DATASET        \n")
        f.write("====================================================================\n\n")
        f.write(f"Total gambar tercatat : {len(metadata_rows)}\n\n")
        
        f.write("1. DUPLIKASI FILE BINER IDENTIK (MD5 Checksum Sama Persis)\n")
        f.write("   File-file ini memiliki hash biner yang sama persis (salinan langsung):\n")
        for g in duplicate_md5_list:
            f.write(f"   * Kelompok {g['group_id']} (MD5: {g['md5']}):\n")
            for f_item in g['files']:
                f.write(f"       - [{f_item['label']}] {f_item['filename']}\n")
        f.write(f"   Total kelompok file identik: {len(duplicate_md5_list)}\n\n")
        
        f.write("2. ANALISIS KEMIRIPAN VISUAL dHash BERDASARKAN JARAK HAMMING\n")
        f.write("   Keterangan Ambang Batas (Threshold):\n")
        f.write("   - Jarak Hamming = 0 : Identik visual (contoh: pasangan format HEIC & JPG)\n")
        f.write("   - Jarak Hamming 1-5 : Sangat mirip visual (burst photos, sudut hampir identik)\n\n")
        
        f.write("   A. Pasangan Identik Visual (Jarak Hamming = 0):\n")
        dist_0 = [p for p in pairwise_similar if p['hamming_distance'] == 0]
        for p in dist_0:
            f.write(f"      - [{p['file1']['label']}] {p['file1']['filename']} <==> [{p['file2']['label']}] {p['file2']['filename']}\n")
        f.write(f"      Total pasangan: {len(dist_0)}\n\n")
        
        f.write("   B. Pasangan Sangat Mirip Visual (Jarak Hamming 1 s/d 5):\n")
        dist_1_5 = [p for p in pairwise_similar if 1 <= p['hamming_distance'] <= 5]
        for p in dist_1_5:
            f.write(f"      - [Jarak {p['hamming_distance']}] [{p['file1']['label']}] {p['file1']['filename']} <==> [{p['file2']['label']}] {p['file2']['filename']}\n")
        f.write(f"      Total pasangan: {len(dist_1_5)}\n\n")
        
    return df_features, failed_images, csv_temp_path, json_report_path, txt_report_path, failed_report_path

if __name__ == '__main__':
    df, failed, csv_path, json_path, txt_path, failed_path = extract_rgb_features()
    print("\n" + "="*50, flush=True)
    print("HASIL EKSTRAKSI FITUR STATISTIK RGB", flush=True)
    print("="*50, flush=True)
    print(f"Total baris berhasil diekstraksi : {len(df)}", flush=True)
    print(f"Total gambar gagal diproses      : {len(failed)}", flush=True)
    print(f"Dimensi DataFrame (shape)        : {df.shape}", flush=True)
    print(f"\nDistribusi label per kelas       :\n{df['label'].value_counts()}", flush=True)
    print("\nPemeriksaan Missing Value (NaN):", flush=True)
    print(df.isna().sum(), flush=True)
    
    print("\nPemeriksaan Finiteness (Apakah ada Inf?):", flush=True)
    inf_count = np.isinf(df.drop(columns=['label'])).sum().sum()
    print(f"Jumlah nilai Infinity: {inf_count}", flush=True)
    
    print("\nStatistik Deskriptif Fitur (Min, Max, Mean):", flush=True)
    feature_cols = [c for c in df.columns if c != 'label']
    stats_df = pd.DataFrame({
        'Min': df[feature_cols].min(),
        'Max': df[feature_cols].max(),
        'Mean': df[feature_cols].mean()
    })
    print(stats_df, flush=True)
    print(f"\nLokasi file CSV sementara        : {csv_path}", flush=True)
    print(f"Lokasi laporan duplikasi (JSON)  : {json_path}", flush=True)
    print(f"Lokasi laporan duplikasi (TXT)   : {txt_path}", flush=True)
    if failed:
        print(f"Lokasi laporan gambar gagal      : {failed_path}", flush=True)
