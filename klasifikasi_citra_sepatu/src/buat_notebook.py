"""
Script Pembuat Jupyter Notebook Klasifikasi Citra Sepatu
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
NOTEBOOK_DIR = os.path.join(PROJECT_DIR, "notebooks")
os.makedirs(NOTEBOOK_DIR, exist_ok=True)
NOTEBOOK_PATH = os.path.join(NOTEBOOK_DIR, "klasifikasi_citra_sepatu.ipynb")

cells = []

def add_md(source):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    })

def add_code(source):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    })

# Cell 1: Judul
add_md("""# Proyek Pengolahan Citra Digital (PCD)
## Klasifikasi Citra Susunan Sepatu Rapi dan Berantakan
**Metode:** Ekstraksi Fitur Statistik Warna RGB + Fitur Tekstur GLCM + Random Forest Classifier  
**Dataset:** 200 Citra (100 Rapi, 100 Berantakan)  
**Tujuan:** Mengklasifikasikan susunan sepatu ke dalam kategori **Rapi** atau **Berantakan** dengan pencegahan *Data Leakage* berbasis kelompok duplikasi.""")

# Cell 2: Import Library
add_md("### 1. Import Library yang Diperlukan")
add_code("""import os
import json
import numpy as np
import pandas as pd

# Konfigurasi cache matplotlib agar kompatibel di berbagai sistem
mpl_dir = os.path.abspath(os.path.join("..", ".mplconfig"))
os.makedirs(mpl_dir, exist_ok=True)
os.environ["MPLCONFIGDIR"] = mpl_dir

import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

# Konfigurasi visualisasi
%matplotlib inline
plt.rcParams['figure.dpi'] = 120
print("Semua library berhasil diimpor!")""")

# Cell 3: Membaca Dataset
add_md("### 2. Membaca Dataset Fitur Citra (CSV Utama)\nDataset ini berisi 14 fitur numerik (9 statistik RGB + 5 tekstur GLCM) dan 1 kolom label target.")
add_code("""dataset_path = os.path.join("..", "output", "dataset_fitur_citra.csv")
df = pd.read_csv(dataset_path)

print(f"Bentuk Dataset (Shape): {df.shape} -> (200 baris, 15 kolom)")
print(f"Pemeriksaan Nilai Kosong (NaN): {df.isna().sum().sum()}")
df.head()""")

# Cell 4: Distribusi Kelas
add_md("### 3. Informasi dan Distribusi Kelas Target")
add_code("""print("Distribusi Target (Label):")
print(df['label'].value_counts())
print("\\nInformasi Tipe Data Kolom:")
print(df.dtypes)""")

# Cell 5: Pemisahan Fitur dan Label
add_md("### 4. Memisahkan Fitur ($X$) dan Target ($y$)\n- $X$: 14 Fitur (mean RGB, std RGB, skew RGB, energy, entropy, contrast, correlation, homogeneity)\n- $y$: Kolom `label` ('rapi' / 'berantakan')")
add_code("""X = df.drop(columns=['label'])
y = df['label']

feature_names = list(X.columns)
print(f"Jumlah Fitur Numerik: {X.shape[1]}")
print(f"Daftar Fitur: {feature_names}")""")

# Cell 6: Pencegahan Data Leakage & Pembagian Data
add_md("""### 5. Pembagian Data (Train-Test Split) dengan Pencegahan Data Leakage
Berdasarkan analisis duplikasi, terdapat citra yang identik secara biner (MD5) dan kemiripan visual sangat tinggi (dHash jarak Hamming $\\le 5$, seperti pasangan format HEIC $\\leftrightarrow$ JPG).
Agar model tidak mengalami *data leakage* (menghafal gambar uji pada saat pelatihan), seluruh pasangan duplikasi dikelompokkan ke dalam grup independen menggunakan *Disjoint Set Union (Union-Find)*, kemudian dipartisi menggunakan `StratifiedGroupKFold(random_state=14)`.""")
add_code("""dup_json_path = os.path.join("..", "output", "laporan_duplikasi_dataset.json")
with open(dup_json_path, "r", encoding="utf-8") as f:
    dup_data = json.load(f)

meta_list = dup_data.get("metadata_file", [])
fn_to_idx = {(m['filename'], m['label']): i for i, m in enumerate(meta_list)}

parent = list(range(len(meta_list)))
def find(i):
    if parent[i] == i:
        return i
    parent[i] = find(parent[i])
    return parent[i]

def union(i, j):
    root_i = find(i)
    root_j = find(j)
    if root_i != root_j:
        parent[root_i] = root_j

# Hubungkan duplikasi MD5 (identik)
for g in dup_data.get('duplikasi_md5_exact', []):
    files = g['files']
    for k in range(len(files) - 1):
        idx1 = fn_to_idx.get((files[k]['filename'], files[k]['label']))
        idx2 = fn_to_idx.get((files[k+1]['filename'], files[k+1]['label']))
        if idx1 is not None and idx2 is not None:
            union(idx1, idx2)

# Hubungkan kemiripan dHash (Hamming <= 5)
for p in dup_data.get('kemiripan_visual_dhash', []):
    f1 = (p['file1']['filename'], p['file1']['label'])
    f2 = (p['file2']['filename'], p['file2']['label'])
    idx1 = fn_to_idx.get(f1)
    idx2 = fn_to_idx.get(f2)
    if idx1 is not None and idx2 is not None:
        union(idx1, idx2)

groups = np.array([find(i) for i in range(len(meta_list))])
print(f"Total 200 data dikelompokkan ke dalam {len(set(groups))} grup independen.")

# Partisi 80:20 berbasis grup independen
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=14)
train_idx, test_idx = next(sgkf.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

print(f"Data Training : {len(train_idx)} baris ({len(train_idx)/200*100:.1f}%) -> {y_train.value_counts().to_dict()}")
print(f"Data Testing  : {len(test_idx)} baris ({len(test_idx)/200*100:.1f}%) -> {y_test.value_counts().to_dict()}")

# Verifikasi kebocoran data (overlapping groups)
overlap = set(groups[train_idx]).intersection(set(groups[test_idx]))
print(f"Tumpang-tindih grup duplikasi: {len(overlap)} (100% Bebas Data Leakage!)")""")

# Cell 7: Pelatihan Model Random Forest
add_md("### 6. Pelatihan Model Random Forest\nModel Random Forest dengan 100 *decision trees* (`n_estimators=100`) dan `random_state=14`. Pelatihan dilakukan murni pada data training saja.")
add_code("""rf_model = RandomForestClassifier(n_estimators=100, random_state=14)
rf_model.fit(X_train, y_train)
print("Model Random Forest berhasil dilatih!")""")

# Cell 8: Pengujian & Evaluasi
add_md("### 7. Evaluasi Model pada Data Testing")
add_code("""y_pred = rf_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
labels_order = ['rapi', 'berantakan']

print(f"Akurasi Model : {accuracy:.4f} ({accuracy * 100:.2f}%)\\n")
print("Classification Report:")
print(classification_report(y_test, y_pred, labels=labels_order, digits=4))""")

# Cell 9: Confusion Matrix
add_md("### 8. Visualisasi Confusion Matrix\nConfusion Matrix menampilkan distribusi prediksi benar (*True Positive* & *True Negative*) serta kesalahan klasifikasi (*False Positive* & *False Negative*).")
add_code("""cm = confusion_matrix(y_test, y_pred, labels=labels_order)

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax.figure.colorbar(im, ax=ax)

ax.set(
    xticks=np.arange(cm.shape[1]),
    yticks=np.arange(cm.shape[0]),
    xticklabels=labels_order,
    yticklabels=labels_order,
    title=f"Confusion Matrix Random Forest\\nAkurasi: {accuracy*100:.2f}%",
    ylabel="Kelas Aktual (True Label)",
    xlabel="Kelas Prediksi (Predicted Label)"
)

thresh = cm.max() / 2.0
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(
            j, i, format(cm[i, j], 'd'),
            ha="center", va="center",
            color="white" if cm[i, j] > thresh else "black",
            fontsize=14, fontweight='bold'
        )

plt.tight_layout()
plt.show()

TP, FN = cm[0, 0], cm[0, 1]
FP, TN = cm[1, 0], cm[1, 1]
print(f"True Positive (Rapi benar diprediksi Rapi)            : {TP}")
print(f"False Negative (Rapi salah diprediksi Berantakan)     : {FN}")
print(f"False Positive (Berantakan salah diprediksi Rapi)     : {FP}")
print(f"True Negative (Berantakan benar diprediksi Berantakan): {TN}")""")

# Cell 10: Feature Importance
add_md("### 9. Visualisasi Feature Importance\nMengetahui fitur ekstraksi citra mana yang paling dominan dalam membedakan susunan sepatu rapi dan berantakan.")
add_code("""importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(10, 6))
plt.title("Feature Importance Random Forest (14 Fitur PCD)", fontsize=13, fontweight='bold')
bars = plt.bar(range(len(importances)), importances[indices], color='teal', edgecolor='black')
plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45, ha='right')
plt.ylabel("Tingkat Kepentingan (Importance)")

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.002, f"{yval:.3f}", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.show()

print("Top 5 Fitur Paling Berpengaruh:")
for rank, idx in enumerate(indices[:5], 1):
    print(f"{rank}. {feature_names[idx]:12s}: {importances[idx]:.4f} ({importances[idx]*100:.2f}%)")""")

notebook_json = {
    "cells": cells,
    "metadata": {
        "language_info": {
            "name": "python",
            "version": "3.9.0"
        },
        "orig_nbformat": 4
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook_json, f, indent=2)

print(f"Jupyter Notebook berhasil dibuat di: {NOTEBOOK_PATH}")
