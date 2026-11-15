"""
Script Ekstraksi Lima Fitur Tekstur GLCM (Tahap 5)
Proyek PCD: Klasifikasi Citra Sepatu Rapi dan Berantakan
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from PIL import Image
from skimage.feature import graycomatrix, graycoprops

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) # Folder: Klasifikasi_Citra_Sepatu
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
GRAYSCALE_DIR = os.path.join(OUTPUT_DIR, "grayscale")
RGB_METADATA_PATH = os.path.join(OUTPUT_DIR, "laporan_duplikasi_dataset.json")

# Parameter GLCM yang konsisten
DISTANCES = [1]
ANGLES = [0, np.pi/4, np.pi/2, 3*np.pi/4] # 0, 45, 90, 135 derajat
LEVELS = 256
SYMMETRIC = True
NORMED = True

def validate_prerequisites():
    if not os.path.exists(RGB_METADATA_PATH):
        raise FileNotFoundError(f"[ERROR] File metadata Tahap 3 tidak ditemukan di: {RGB_METADATA_PATH}")
    if not os.path.isdir(GRAYSCALE_DIR):
        raise FileNotFoundError(f"[ERROR] Folder grayscale Tahap 4 tidak ditemukan di: {GRAYSCALE_DIR}")
    print("[VALIDASI] Metadata urutan Tahap 3 dan folder citra grayscale Tahap 4 terverifikasi.")

def compute_glcm_entropy(glcm_normalized):
    """
    Menghitung entropy untuk setiap sudut k dari matriks GLCM yang telah dinormalisasi:
    H_k = - sum_{i,j} P(i,j) * log2(P(i,j))
    Elemen dengan probabilitas nol (P=0) diabaikan secara matematis karena lim_{p->0+} p * log2(p) = 0.
    Mengembalikan rata-rata entropy dari keempat sudut.
    """
    num_angles = glcm_normalized.shape[3]
    entropies = []
    for k in range(num_angles):
        # Matriks probabilitas 2D untuk sudut ke-k (256 x 256)
        P_k = glcm_normalized[:, :, 0, k]
        # Ambil hanya elemen dengan probabilitas > 0
        nonzero_p = P_k[P_k > 0]
        # Hitung - sum(P * log2(P))
        h_k = -np.sum(nonzero_p * np.log2(nonzero_p))
        entropies.append(float(h_k))
    return float(np.mean(entropies)), entropies

def extract_glcm_features():
    validate_prerequisites()
    
    # Baca metadata Tahap 3 untuk memastikan urutan baris sama persis dengan CSV RGB
    with open(RGB_METADATA_PATH, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
    
    metadata_list = meta_data.get("metadata_file", [])
    if len(metadata_list) != 200:
        raise ValueError(f"Jumlah metadata file pada Tahap 3 ({len(metadata_list)}) tidak sesuai target 200.")
        
    print(f"\n[MEMULAI EKSTRAKSI GLCM] Memproses 200 citra grayscale sesuai urutan CSV RGB...", flush=True)
    
    csv_rows = []
    detailed_metadata = []
    failed_items = []
    
    for idx, item in enumerate(metadata_list):
        orig_filename = item["filename"]
        label = item["label"]
        
        # Penentuan nama file di folder grayscale
        base_name, ext = os.path.splitext(orig_filename)
        if ext.lower() == ".heic":
            gray_filename = f"{base_name}.png"
        else:
            gray_filename = orig_filename
            
        gray_filepath = os.path.join(GRAYSCALE_DIR, label, gray_filename)
        
        if not os.path.isfile(gray_filepath):
            failed_items.append({
                'index': idx,
                'filename': orig_filename,
                'label': label,
                'error': f"File grayscale tidak ditemukan: {gray_filepath}"
            })
            continue
            
        try:
            with Image.open(gray_filepath) as img:
                # Pastikan mode 'L'
                if img.mode != 'L':
                    img = img.convert('L')
                img_arr = np.array(img, dtype=np.uint8)
                
                # Validasi bentuk citra 2D dan rentang
                if len(img_arr.shape) != 2:
                    raise ValueError(f"Dimensi citra bukan 2D: {img_arr.shape}")
                if img_arr.dtype != np.uint8:
                    raise ValueError(f"Tipe data bukan uint8: {img_arr.dtype}")
                    
                # 1. Hitung matriks GLCM
                glcm = graycomatrix(
                    img_arr,
                    distances=DISTANCES,
                    angles=ANGLES,
                    levels=LEVELS,
                    symmetric=SYMMETRIC,
                    normed=NORMED
                )
                
                # 2. ENERGY
                # graycoprops 'energy' menghitung sqrt(ASM) untuk masing-masing sudut
                energy_per_angle = graycoprops(glcm, 'energy')[0]
                energy = float(np.mean(energy_per_angle))
                
                # 3. ENTROPY
                # Dihitung secara manual dari matriks probabilitas yang telah dinormalisasi
                entropy, entropy_per_angle = compute_glcm_entropy(glcm)
                
                # 4. CONTRAST
                contrast_per_angle = graycoprops(glcm, 'contrast')[0]
                contrast = float(np.mean(contrast_per_angle))
                
                # 5. CORRELATION
                correlation_per_angle = graycoprops(glcm, 'correlation')[0]
                # Periksa apakah ada nilai NaN pada sudut tertentu (misal varians lokal = 0)
                if any(np.isnan(c) for c in correlation_per_angle):
                    raise ValueError(f"Correlation menghasilkan NaN pada sudut: {correlation_per_angle}")
                correlation = float(np.mean(correlation_per_angle))
                
                # 6. HOMOGENEITY
                homogeneity_per_angle = graycoprops(glcm, 'homogeneity')[0]
                homogeneity = float(np.mean(homogeneity_per_angle))
                
                # Validasi finiteness seluruh fitur
                feature_vals = [energy, entropy, contrast, correlation, homogeneity]
                if not all(np.isfinite(v) for v in feature_vals):
                    raise ValueError(f"Fitur tidak finite ditemukan: {feature_vals}")
                    
                # Baris CSV utama: Tepat 6 kolom (5 fitur numerik + 1 label)
                csv_rows.append({
                    'energy': energy,
                    'entropy': entropy,
                    'contrast': contrast,
                    'correlation': correlation,
                    'homogeneity': homogeneity,
                    'label': label
                })
                
                # Metadata detail disimpan terpisah
                detailed_metadata.append({
                    'index': idx,
                    'original_filename': orig_filename,
                    'grayscale_filename': gray_filename,
                    'label': label,
                    'features': {
                        'energy': energy,
                        'entropy': entropy,
                        'contrast': contrast,
                        'correlation': correlation,
                        'homogeneity': homogeneity
                    },
                    'per_angle': {
                        'energy': [float(x) for x in energy_per_angle],
                        'entropy': entropy_per_angle,
                        'contrast': [float(x) for x in contrast_per_angle],
                        'correlation': [float(x) for x in correlation_per_angle],
                        'homogeneity': [float(x) for x in homogeneity_per_angle]
                    }
                })
                
        except Exception as e:
            failed_items.append({
                'index': idx,
                'filename': orig_filename,
                'label': label,
                'error': str(e)
            })
            print(f"  [ERROR] Index {idx} ({orig_filename}): {e}", flush=True)
            
        if (idx + 1) % 40 == 0:
            print(f"  Progress: {idx + 1}/200 citra selesai diekstraksi fitur GLCM...", flush=True)
            
    # Simpan CSV sementara fitur GLCM (tepat 6 kolom, tanpa nama file)
    df_glcm = pd.DataFrame(csv_rows)
    csv_glcm_path = os.path.join(OUTPUT_DIR, "fitur_glcm_sementara.csv")
    df_glcm.to_csv(csv_glcm_path, index=False)
    
    # Simpan metadata JSON terpisah
    json_meta_path = os.path.join(OUTPUT_DIR, "metadata_glcm.json")
    with open(json_meta_path, "w", encoding="utf-8") as f:
        json.dump({
            'total_items': len(detailed_metadata),
            'parameters': {
                'distances': DISTANCES,
                'angles_rad': [float(a) for a in ANGLES],
                'angles_deg': [0, 45, 90, 135],
                'levels': LEVELS,
                'symmetric': SYMMETRIC,
                'normed': NORMED
            },
            'items': detailed_metadata
        }, f, indent=2)
        
    # Simpan laporan GLCM TXT
    report_glcm_path = os.path.join(OUTPUT_DIR, "laporan_glcm.txt")
    with open(report_glcm_path, "w", encoding="utf-8") as f:
        f.write("====================================================================\n")
        f.write("            LAPORAN EKSTRAKSI LIMA FITUR TEKSTUR GLCM               \n")
        f.write("====================================================================\n\n")
        f.write(f"Total citra berhasil diekstraksi : {len(df_glcm)}\n")
        f.write(f"Total citra gagal                : {len(failed_items)}\n")
        f.write(f"Dimensi DataFrame CSV            : {df_glcm.shape} (200 baris, 6 kolom)\n\n")
        
        f.write("1. PARAMETER GLCM:\n")
        f.write("   - Jarak piksel (distances)    : [1]\n")
        f.write("   - Arah sudut (angles)         : 4 sudut [0, 45, 90, 135] derajat (dalam radian)\n")
        f.write("   - Nilai aras keabuan (levels) : 256 (sesuai citra grayscale 8-bit)\n")
        f.write("   - Matriks simetris (symmetric): True (menghitung pasangan bolak-balik)\n")
        f.write("   - Normalisasi (normed)        : True (matriks berupa nilai probabilitas sum=1)\n")
        f.write("   - Agregasi sudut              : Rata-rata aritmatika dari keempat sudut\n\n")
        
        f.write("2. DEFINISI DAN METODE PERHITUNGAN FITUR:\n")
        f.write("   a. ENERGY:\n")
        f.write("      Mengukur keseragaman distribusi intensitas pada matriks GLCM.\n")
        f.write("      Dihitung melalui graycoprops(glcm, 'energy') sebagai akar kuadrat dari\n")
        f.write("      Angular Second Moment (ASM): Energy = sqrt(sum_{i,j} P(i,j)^2).\n")
        f.write("   b. ENTROPY:\n")
        f.write("      Mengukur keacakan atau kompleksitas tekstur citra.\n")
        f.write("      Dihitung secara manual per sudut: H = - sum_{i,j} P(i,j) * log2(P(i,j))\n")
        f.write("      dengan mengabaikan elemen berprobabilitas nol (P=0), lalu dirata-ratakan.\n")
        f.write("   c. CONTRAST:\n")
        f.write("      Mengukur besarnya variasi lokal intensitas piksel berpasangan:\n")
        f.write("      Contrast = sum_{i,j} |i - j|^2 * P(i,j).\n")
        f.write("   d. CORRELATION:\n")
        f.write("      Mengukur ketergantungan linear aras keabuan antar piksel berdekatan:\n")
        f.write("      Correlation = sum_{i,j} (i - mu_i)*(j - mu_j)*P(i,j) / (sigma_i * sigma_j).\n")
        f.write("   e. HOMOGENEITY:\n")
        f.write("      Mengukur kedekatan distribusi elemen GLCM terhadap diagonal utama:\n")
        f.write("      Homogeneity = sum_{i,j} P(i,j) / (1 + |i - j|).\n\n")
        
        f.write("3. DISTRIBUSI KELAS DATA:\n")
        for lbl in ['rapi', 'berantakan']:
            cnt = (df_glcm['label'] == lbl).sum()
            f.write(f"   - Label '{lbl}': {cnt} baris data\n")
        f.write("\n")
        
        f.write("4. PEMERIKSAAN NILAI TIDAK VALID (NaN / Infinity):\n")
        f.write(f"   - Missing Values (NaN)  : {df_glcm.isna().sum().sum()} nilai\n")
        inf_cnt = np.isinf(df_glcm.drop(columns=['label'])).sum().sum()
        f.write(f"   - Nilai Infinity (Inf)  : {inf_cnt} nilai\n")
        f.write("   - Seluruh nilai fitur berstatus valid dan finite.\n\n")
        
        f.write("5. STATISTIK DESKRIPTIF FITUR GLCM (MIN, MAX, MEAN):\n")
        feat_cols = ['energy', 'entropy', 'contrast', 'correlation', 'homogeneity']
        stats_df = pd.DataFrame({
            'Min': df_glcm[feat_cols].min(),
            'Max': df_glcm[feat_cols].max(),
            'Mean': df_glcm[feat_cols].mean()
        })
        f.write(stats_df.to_string())
        f.write("\n\n")
        
        f.write("6. LOKASI PENYIMPANAN FILE:\n")
        f.write(f"   - CSV Fitur GLCM Sementara : {csv_glcm_path}\n")
        f.write(f"   - File Metadata Detail     : {json_meta_path}\n")
        f.write(f"   - File Laporan Teks        : {report_glcm_path}\n")
        
    print(f"\n[SELESAI] Ekstraksi GLCM berhasil disimpan di: {csv_glcm_path}", flush=True)
    return df_glcm, failed_items, csv_glcm_path, json_meta_path, report_glcm_path

if __name__ == '__main__':
    df, failed, csv_p, json_p, rep_p = extract_glcm_features()
    print("\n" + "="*50)
    print("HASIL VALIDASI EKSTRAKSI LIMA FITUR GLCM")
    print("="*50)
    print(f"Total baris data : {len(df)}")
    print(f"Total gagal      : {len(failed)}")
    print(f"Dimensi shape    : {df.shape}")
    print(f"Kolom CSV        : {df.columns.tolist()}")
    print("\nDistribusi Label :")
    print(df['label'].value_counts())
    print("\nPemeriksaan NaN  :")
    print(df.isna().sum())
    print("\nStatistik Fitur GLCM (Min, Max, Mean):")
    feat_cols = ['energy', 'entropy', 'contrast', 'correlation', 'homogeneity']
    stats_df = pd.DataFrame({
        'Min': df[feat_cols].min(),
        'Max': df[feat_cols].max(),
        'Mean': df[feat_cols].mean()
    })
    print(stats_df)

