"""
Script Pemeriksaan dan Pembacaan Dataset Citra Sepatu (Tahap 2)
Proyek PCD: Klasifikasi Citra Sepatu Rapi dan Berantakan
"""

import os
import hashlib
from collections import defaultdict
import numpy as np
from PIL import Image
import pillow_heif

# Register heif opener agar PIL dapat membaca .heic
pillow_heif.register_heif_opener()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PARENT_DIR = os.path.dirname(PROJECT_DIR)

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

def compute_dhash(image, hash_size=8):
    """Menghitung difference hash (dHash) untuk mendeteksi kesamaan visual citra."""
    # Resize ke (hash_size + 1, hash_size) lalu grayscale
    resized = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized)
    # Perbandingan kolom berdekatan
    difference = pixels[:, 1:] > pixels[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(difference.flatten()) if v])

def compute_file_md5(file_path):
    """Menghitung MD5 checksum dari file asli."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def inspect_dataset():
    results = {
        'total_found': 0,
        'total_success': 0,
        'total_failed': 0,
        'by_class': defaultdict(lambda: {'success': 0, 'failed': 0, 'formats': defaultdict(int)}),
        'failed_details': [],
        'dimensions': defaultdict(list),
        'pixel_ranges': [],
        'dtypes': set(),
        'dhashes': defaultdict(list), # dhash -> list of (class, filename)
        'file_md5s': defaultdict(list),
        'items': []
    }

    for label, folder_path in DATASET_PATHS.items():
        print(f"\n[MEMERIKSA FOLDER] {label.upper()}: {folder_path}")
        if not os.path.exists(folder_path):
            print(f"ERROR: Folder tidak ditemukan: {folder_path}")
            continue

        filenames = sorted(os.listdir(folder_path))
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue

            results['total_found'] += 1
            ext = os.path.splitext(filename)[1].lower()
            results['by_class'][label]['formats'][ext] += 1

            # Hitung MD5 file
            f_md5 = compute_file_md5(file_path)
            results['file_md5s'][f_md5].append((label, filename))

            try:
                with Image.open(file_path) as img:
                    orig_format = img.format
                    orig_mode = img.mode
                    orig_size = img.size # (width, height)

                    # Konversi ke format RGB (sesuai ketentuan 5)
                    rgb_img = img.convert('RGB')
                    img_array = np.array(rgb_img)

                    # Validasi bentuk, channel, tipe data, rentang piksel
                    shape = img_array.shape # (height, width, channels)
                    dtype = str(img_array.dtype)
                    min_val = int(np.min(img_array))
                    max_val = int(np.max(img_array))

                    results['dtypes'].add(dtype)
                    results['pixel_ranges'].append((min_val, max_val))
                    results['dimensions'][label].append((shape[1], shape[0])) # (width, height)

                    # Perceptual hash untuk cek duplikasi visual
                    dh = compute_dhash(rgb_img, hash_size=8)
                    results['dhashes'][dh].append((label, filename))

                    results['total_success'] += 1
                    results['by_class'][label]['success'] += 1

                    results['items'].append({
                        'label': label,
                        'filename': filename,
                        'ext': ext,
                        'orig_mode': orig_mode,
                        'orig_size': orig_size,
                        'rgb_shape': shape,
                        'dtype': dtype,
                        'min_val': min_val,
                        'max_val': max_val,
                        'dhash': dh
                    })

            except Exception as e:
                results['total_failed'] += 1
                results['by_class'][label]['failed'] += 1
                results['failed_details'].append({
                    'label': label,
                    'filename': filename,
                    'error': str(e)
                })
                print(f"  [GAGAL] {filename}: {e}")

    return results

if __name__ == '__main__':
    res = inspect_dataset()
    print("\n" + "="*50)
    print("HASIL PEMERIKSAAN DAN PEMBACAAN DATASET")
    print("="*50)
    print(f"Total gambar ditemukan : {res['total_found']}")
    print(f"Total berhasil dibaca  : {res['total_success']}")
    print(f"Total gagal dibaca     : {res['total_failed']}")

    for label in ['rapi', 'berantakan']:
        info = res['by_class'][label]
        print(f"\nKelas: {label.upper()}")
        print(f"  - Berhasil dibaca : {info['success']}")
        print(f"  - Gagal dibaca    : {info['failed']}")
        print(f"  - Format rincian  : {dict(info['formats'])}")

    print(f"\nTipe data array numpy  : {res['dtypes']}")
    all_mins = [p[0] for p in res['pixel_ranges']]
    all_maxs = [p[1] for p in res['pixel_ranges']]
    print(f"Rentang nilai piksel   : [{min(all_mins)}, {max(all_maxs)}]")

    # Cek duplikat MD5
    md5_dups = {k: v for k, v in res['file_md5s'].items() if len(v) > 1}
    print(f"\nDuplikasi file exact (MD5 sama): {len(md5_dups)}")
    for md5_val, files in md5_dups.items():
        print(f"  MD5 {md5_val}: {files}")

    # Cek duplikat visual dHash
    dhash_dups = {k: v for k, v in res['dhashes'].items() if len(v) > 1}
    print(f"\nDuplikasi visual potensial (dHash sama): {len(dhash_dups)}")
    for h, files in dhash_dups.items():
        print(f"  dHash {hex(h)}: {files}")

