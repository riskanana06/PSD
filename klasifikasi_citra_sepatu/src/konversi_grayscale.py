"""
Script Konversi Grayscale 8-bit (Tahap 4)
Proyek PCD: Klasifikasi Citra Sepatu Rapi dan Berantakan
"""

import os
import sys
import numpy as np
from PIL import Image
import pillow_heif

# Registrasi heif opener agar PIL dapat membaca .heic
pillow_heif.register_heif_opener()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) # Folder: klasifikasi_citra_sepatu
PARENT_DIR = os.path.dirname(PROJECT_DIR)  # Folder: PSD (atau psd new)
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
GRAYSCALE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "grayscale")

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

def validate_paths():
    for label, folder_path in DATASET_PATHS.items():
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f"Folder dataset '{label}' tidak ditemukan di: {folder_path}")
        out_sub = os.path.join(GRAYSCALE_OUTPUT_DIR, label)
        os.makedirs(out_sub, exist_ok=True)
    print("[VALIDASI] Direktori dataset input dan output grayscale berhasil diverifikasi.")

def convert_to_grayscale():
    validate_paths()
    
    conversion_results = []
    failed_conversions = []
    
    for label in ['rapi', 'berantakan']:
        input_folder = DATASET_PATHS[label]
        output_folder = os.path.join(GRAYSCALE_OUTPUT_DIR, label)
        filenames = sorted(os.listdir(input_folder))
        
        print(f"\n[KONVERSI GRAYSCALE] Kategori {label.upper()} ({len(filenames)} file)...", flush=True)
        
        for idx, filename in enumerate(filenames):
            input_path = os.path.join(input_folder, filename)
            if not os.path.isfile(input_path):
                continue
                
            base_name, ext = os.path.splitext(filename)
            ext_lower = ext.lower()
            
            # Ketentuan nama file simpan:
            # Format HEIC disimpan sebagai PNG dengan nama dasar yang sama
            # Format JPG/JPEG disimpan dengan nama dan ekstensi yang sama
            if ext_lower == '.heic':
                out_filename = f"{base_name}.png"
            else:
                out_filename = filename
                
            out_path = os.path.join(output_folder, out_filename)
            
            # Pastikan tidak ada konflik/penimpaan yang tidak disengaja
            if os.path.exists(out_path):
                # jika file sudah ada sebelumnya dari run lama, kita overwrite secara terkendali
                pass
                
            try:
                # 1. Buka citra asli
                with Image.open(input_path) as img:
                    orig_size = img.size # (width, height)
                    orig_mode = img.mode
                    
                    # 2. Konversi ke Grayscale 8-bit (mode 'L')
                    # Mode 'L' pada Pillow menerapkan ITU-R 601-2 luma transform:
                    # L = R * 299/1000 + G * 587/1000 + B * 114/1000
                    gray_img = img.convert('L')
                    gray_size = gray_img.size
                    
                    # Validasi dimensi sebelum dan sesudah konversi
                    if orig_size != gray_size:
                        raise ValueError(f"Dimensi berubah: aslinya {orig_size}, hasil {gray_size}")
                    
                    # Simpan citra grayscale
                    if ext_lower == '.heic':
                        gray_img.save(out_path, format='PNG')
                    elif ext_lower in ['.jpg', '.jpeg']:
                        # Simpan sebagai JPEG grayscale berkualitas tinggi tanpa subsampling warna
                        gray_img.save(out_path, format='JPEG', quality=95)
                    else:
                        gray_img.save(out_path)
                        
                # 3. Uji baca kembali (Verifikasi file tersimpan)
                with Image.open(out_path) as saved_img:
                    saved_mode = saved_img.mode
                    saved_size = saved_img.size
                    saved_arr = np.array(saved_img)
                    
                    # Validasi karakteristik:
                    # - Mode 'L'
                    # - 1 channel (array 2 dimensi: height x width)
                    # - Tipe data uint8
                    # - Rentang piksel dalam [0, 255]
                    is_mode_L = (saved_mode == 'L')
                    is_2d = (len(saved_arr.shape) == 2)
                    is_uint8 = (saved_arr.dtype == np.uint8)
                    min_val = int(np.min(saved_arr))
                    max_val = int(np.max(saved_arr))
                    is_range_valid = (0 <= min_val <= 255) and (0 <= max_val <= 255)
                    
                    if not (is_mode_L and is_2d and is_uint8 and is_range_valid):
                        raise ValueError(f"Validasi gagal: mode={saved_mode}, shape={saved_arr.shape}, dtype={saved_arr.dtype}, range=[{min_val}, {max_val}]")
                        
                    conversion_results.append({
                        'label': label,
                        'original_filename': filename,
                        'grayscale_filename': out_filename,
                        'original_ext': ext_lower,
                        'output_path': out_path,
                        'width': saved_size[0],
                        'height': saved_size[1],
                        'mode': saved_mode,
                        'dtype': str(saved_arr.dtype),
                        'min_val': min_val,
                        'max_val': max_val
                    })
                    
            except Exception as e:
                failed_conversions.append({
                    'label': label,
                    'filename': filename,
                    'error': str(e)
                })
                print(f"  [GAGAL] {filename}: {e}", flush=True)
                
            if (idx + 1) % 25 == 0:
                print(f"  Progress: {idx + 1}/100 file kategori {label} selesai dikonversi...", flush=True)
                
    # Buat file laporan
    report_path = os.path.join(OUTPUT_DIR, "laporan_grayscale.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("====================================================================\n")
        f.write("             LAPORAN HASIL KONVERSI CITRA GRAYSCALE 8-BIT           \n")
        f.write("====================================================================\n\n")
        f.write(f"Total gambar berhasil dikonversi : {len(conversion_results)}\n")
        f.write(f"Total gambar gagal dikonversi    : {len(failed_conversions)}\n\n")
        
        f.write("1. DISTRIBUSI PER KATEGORI:\n")
        for label in ['rapi', 'berantakan']:
            count = sum(1 for r in conversion_results if r['label'] == label)
            f.write(f"   - Kategori {label.upper():10s}: {count} gambar\n")
        f.write("\n")
        
        f.write("2. KARAKTERISTIK CITRA GRAYSCALE HASIL KONVERSI:\n")
        f.write("   - Mode citra          : L (8-bit grayscale)\n")
        f.write("   - Jumlah channel      : 1 channel (matriks 2 dimensi)\n")
        f.write("   - Tipe data array     : uint8 (unsigned integer 8-bit)\n")
        all_mins = [r['min_val'] for r in conversion_results]
        all_maxs = [r['max_val'] for r in conversion_results]
        f.write(f"   - Rentang nilai piksel: [{min(all_mins)}, {max(all_maxs)}]\n")
        f.write("   - Integritas dimensi  : 100% resolusi citra sama persis dengan citra asli\n\n")
        
        f.write("3. STRUKTUR DAN LOKASI PENYIMPANAN:\n")
        f.write(f"   - Folder Utama        : {GRAYSCALE_OUTPUT_DIR}\n")
        f.write(f"   - Subfolder Rapi      : {os.path.join(GRAYSCALE_OUTPUT_DIR, 'rapi')}\n")
        f.write(f"   - Subfolder Berantakan: {os.path.join(GRAYSCALE_OUTPUT_DIR, 'berantakan')}\n\n")
        
        f.write("4. PENANGANAN FORMAT HEIC (6 File):\n")
        f.write("   Karena format HEIC tidak mendukung penyimpanan langsung grayscale pada Pillow,\n")
        f.write("   keenam file HEIC dikonversi dan disimpan dalam format PNG lossless dengan nama dasar sama:\n")
        heic_conversions = [r for r in conversion_results if r['original_ext'] == '.heic']
        for hc in heic_conversions:
            f.write(f"   * [{hc['label']}] Asli: '{hc['original_filename']}' -> Hasil: '{hc['grayscale_filename']}'\n")
        f.write("\n")
        
        if failed_conversions:
            f.write("5. DAFTAR GAMBAR GAGAL:\n")
            for fc in failed_conversions:
                f.write(f"   - [{fc['label']}] {fc['filename']}: {fc['error']}\n")
        else:
            f.write("5. STATUS KEGAGALAN:\n   Tidak ada gambar yang gagal (0 file gagal).\n")
            
    print(f"\n[SELESAI] Laporan grayscale disimpan di: {report_path}", flush=True)
    return conversion_results, failed_conversions, report_path

if __name__ == '__main__':
    results, failed, report = convert_to_grayscale()
    print("\n" + "="*50)
    print("HASIL VALIDASI KONVERSI GRAYSCALE")
    print("="*50)
    print(f"Total berhasil : {len(results)}")
    print(f"Total gagal    : {len(failed)}")
    for lbl in ['rapi', 'berantakan']:
        c = sum(1 for r in results if r['label'] == lbl)
        print(f"Kategori {lbl.upper():10s}: {c} gambar")
    all_mins = [r['min_val'] for r in results]
    all_maxs = [r['max_val'] for r in results]
    print(f"Rentang piksel : [{min(all_mins)}, {max(all_maxs)}]")
    print(f"Tipe data      : {set(r['dtype'] for r in results)}")
    print(f"Mode gambar    : {set(r['mode'] for r in results)}")

