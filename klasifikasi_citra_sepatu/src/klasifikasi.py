"""
Script Pembagian Data dan Klasifikasi Random Forest (Tahap 7)
Proyek PCD: Klasifikasi Citra Sepatu Rapi dan Berantakan
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd

# Konfigurasi matplotlib agar aman di dalam sandbox
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) # Folder: Klasifikasi_Citra_Sepatu
MPL_DIR = os.path.join(PROJECT_DIR, ".mplconfig")
os.makedirs(MPL_DIR, exist_ok=True)
os.environ["MPLCONFIGDIR"] = MPL_DIR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
DATASET_CSV_PATH = os.path.join(OUTPUT_DIR, "dataset_fitur_citra.csv")
DUP_JSON_PATH = os.path.join(OUTPUT_DIR, "laporan_duplikasi_dataset.json")

MODEL_SAVE_PATH = os.path.join(OUTPUT_DIR, "model_random_forest.pkl")
REPORT_SAVE_PATH = os.path.join(OUTPUT_DIR, "laporan_klasifikasi.txt")
CM_IMAGE_PATH = os.path.join(OUTPUT_DIR, "confusion_matrix.png")
FEAT_IMP_IMAGE_PATH = os.path.join(OUTPUT_DIR, "feature_importance.png")
EVAL_JSON_PATH = os.path.join(OUTPUT_DIR, "hasil_evaluasi.json")

LABELS_ORDER = ['rapi', 'berantakan']

def build_duplicate_groups(meta_list, dup_data):
    """
    Membangun kelompok komponen terhubung (Disjoint Set Union)
    berdasarkan duplikasi MD5 dan kemiripan dHash (Hamming <= 5).
    """
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
            
    fn_to_idx = {(m['filename'], m['label']): i for i, m in enumerate(meta_list)}
    
    # 1. Hubungkan duplikasi MD5 (identik biner)
    for g in dup_data.get('duplikasi_md5_exact', []):
        files = g['files']
        for k in range(len(files) - 1):
            idx1 = fn_to_idx.get((files[k]['filename'], files[k]['label']))
            idx2 = fn_to_idx.get((files[k+1]['filename'], files[k+1]['label']))
            if idx1 is not None and idx2 is not None:
                union(idx1, idx2)
                
    # 2. Hubungkan kemiripan dHash (Jarak Hamming <= 5)
    for p in dup_data.get('kemiripan_visual_dhash', []):
        f1 = (p['file1']['filename'], p['file1']['label'])
        f2 = (p['file2']['filename'], p['file2']['label'])
        idx1 = fn_to_idx.get(f1)
        idx2 = fn_to_idx.get(f2)
        if idx1 is not None and idx2 is not None:
            union(idx1, idx2)
            
    groups = np.array([find(i) for i in range(len(meta_list))])
    return groups

def plot_confusion_matrix(cm, labels, acc, save_path):
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=labels,
        yticklabels=labels,
        title=f"Confusion Matrix Random Forest\nAkurasi: {acc*100:.2f}%",
        ylabel="Kelas Aktual (True Label)",
        xlabel="Kelas Prediksi (Predicted Label)"
    )
    
    # Tambahkan angka di setiap sel
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=14, fontweight='bold'
            )
            
    fig.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)
    print(f"      Visualisasi Confusion Matrix disimpan di: {save_path}")

def plot_feature_importance(clf, feature_names, save_path):
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_title("Feature Importance Random Forest (14 Fitur PCD)", fontsize=14, fontweight='bold')
    bars = ax.bar(range(len(importances)), importances[indices], color='teal', edgecolor='black')
    ax.set_xticks(range(len(importances)))
    ax.set_xticklabels([feature_names[i] for i in indices], rotation=45, ha='right', fontsize=10)
    ax.set_ylabel("Tingkat Kepentingan (Importance)", fontsize=11)
    
    # Tambahkan label nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)
                    
    fig.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close(fig)
    print(f"      Visualisasi Feature Importance disimpan di: {save_path}")

def run_classification():
    print("[1/5] Membaca dan memvalidasi dataset CSV utama...")
    if not os.path.isfile(DATASET_CSV_PATH):
        raise FileNotFoundError(f"[ERROR] Dataset utama tidak ditemukan di: {DATASET_CSV_PATH}")
    if not os.path.isfile(DUP_JSON_PATH):
        raise FileNotFoundError(f"[ERROR] Metadata duplikasi tidak ditemukan di: {DUP_JSON_PATH}")
        
    df = pd.read_csv(DATASET_CSV_PATH)
    rows, cols = df.shape
    if rows != 200 or cols != 15:
        raise ValueError(f"[ERROR] Dimensi dataset tidak sesuai: {df.shape}, target (200, 15)")
        
    nan_count = df.isna().sum().sum()
    if nan_count > 0:
        raise ValueError(f"[ERROR] Ditemukan {nan_count} missing values (NaN) pada dataset!")
        
    X = df.drop(columns=['label'])
    y = df['label']
    
    inf_count = np.isinf(X).sum().sum()
    if inf_count > 0:
        raise ValueError(f"[ERROR] Ditemukan {inf_count} nilai Infinity pada fitur X!")
        
    print(f"      Dimensi dataset: {df.shape} (200 baris x 15 kolom).")
    print(f"      Distribusi kelas awal:\n{y.value_counts().to_string()}")
    
    print("\n[2/5] Membangun pengelompokan duplikasi untuk pencegahan Data Leakage...")
    with open(DUP_JSON_PATH, "r", encoding="utf-8") as f:
        dup_data = json.load(f)
    meta_list = dup_data.get("metadata_file", [])
    
    groups = build_duplicate_groups(meta_list, dup_data)
    unique_groups = len(set(groups))
    print(f"      Total 200 citra terkelompok ke dalam {unique_groups} grup independen.")
    
    # Pembagian data berbasis Stratified Group K-Fold untuk mencegah data leakage
    # Menggunakan 5-fold (rasio 80:20), random_state=14
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=14)
    train_idx, test_idx = next(sgkf.split(X, y, groups))
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    train_groups = set(groups[train_idx])
    test_groups = set(groups[test_idx])
    overlapping_groups = train_groups.intersection(test_groups)
    
    print(f"\n[3/5] Hasil Pembagian Data (Pencegahan Data Leakage Aktif):")
    print(f"      Data Training : {len(train_idx)} baris ({len(train_idx)/200*100:.1f}%)")
    print(f"                      Distribusi: {y_train.value_counts().to_dict()}")
    print(f"      Data Testing  : {len(test_idx)} baris ({len(test_idx)/200*100:.1f}%)")
    print(f"                      Distribusi: {y_test.value_counts().to_dict()}")
    print(f"      Tumpang-tindih kelompok duplikasi (Data Leakage): {len(overlapping_groups)} grup")
    if len(overlapping_groups) > 0:
        raise ValueError("[ERROR] Terjadi data leakage pada pembagian data!")
    print("      [TERBUKTI] Nol (0) data leakage antara training dan testing.")

    print("\n[4/5] Melatih Model Random Forest (100 Estimator, random_state=14)...")
    clf = RandomForestClassifier(n_estimators=100, random_state=14)
    # Pelatihan strictly menggunakan data training saja tanpa penskalaan (StandardScaler tidak diperlukan)
    clf.fit(X_train, y_train)
    print("      Model Random Forest berhasil dilatih.")

    print("\n[5/5] Melakukan Pengujian dan Evaluasi Model pada Data Testing...")
    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, labels=LABELS_ORDER, average='macro')
    rec_macro = recall_score(y_test, y_pred, labels=LABELS_ORDER, average='macro')
    f1_macro = f1_score(y_test, y_pred, labels=LABELS_ORDER, average='macro')
    
    prec_per_class = precision_score(y_test, y_pred, labels=LABELS_ORDER, average=None)
    rec_per_class = recall_score(y_test, y_pred, labels=LABELS_ORDER, average=None)
    f1_per_class = f1_score(y_test, y_pred, labels=LABELS_ORDER, average=None)
    
    cm = confusion_matrix(y_test, y_pred, labels=LABELS_ORDER)
    report_text = classification_report(y_test, y_pred, labels=LABELS_ORDER, digits=4)
    
    # Hitung TP, FP, FN, TN (dengan kelas positif = 'rapi')
    # labels order: index 0 = 'rapi', index 1 = 'berantakan'
    # cm[0, 0]: True rapi, Pred rapi (TP)
    # cm[0, 1]: True rapi, Pred berantakan (FN)
    # cm[1, 0]: True berantakan, Pred rapi (FP)
    # cm[1, 1]: True berantakan, Pred berantakan (TN)
    TP = int(cm[0, 0])
    FN = int(cm[0, 1])
    FP = int(cm[1, 0])
    TN = int(cm[1, 1])

    # Simpan model Random Forest
    with open(MODEL_SAVE_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"      Model disimpan di: {MODEL_SAVE_PATH}")

    # Simpan visualisasi Confusion Matrix
    plot_confusion_matrix(cm, LABELS_ORDER, acc, CM_IMAGE_PATH)

    # Simpan visualisasi Feature Importance
    plot_feature_importance(clf, list(X.columns), FEAT_IMP_IMAGE_PATH)

    # Simpan hasil evaluasi lengkap ke JSON
    eval_data = {
        'split_info': {
            'strategy': 'StratifiedGroupKFold (Zero Data Leakage)',
            'random_state': 14,
            'train_size': len(train_idx),
            'test_size': len(test_idx),
            'train_class_distribution': y_train.value_counts().to_dict(),
            'test_class_distribution': y_test.value_counts().to_dict(),
            'train_indices': [int(i) for i in train_idx],
            'test_indices': [int(i) for i in test_idx]
        },
        'metrics': {
            'accuracy': float(acc),
            'accuracy_percentage': f"{acc*100:.2f}%",
            'macro_avg': {
                'precision': float(prec_macro),
                'recall': float(rec_macro),
                'f1_score': float(f1_macro)
            },
            'per_class': {
                'rapi': {
                    'precision': float(prec_per_class[0]),
                    'recall': float(rec_per_class[0]),
                    'f1_score': float(f1_per_class[0]),
                    'support': int((y_test == 'rapi').sum())
                },
                'berantakan': {
                    'precision': float(prec_per_class[1]),
                    'recall': float(rec_per_class[1]),
                    'f1_score': float(f1_per_class[1]),
                    'support': int((y_test == 'berantakan').sum())
                }
            },
            'confusion_matrix': {
                'labels': LABELS_ORDER,
                'matrix': cm.tolist(),
                'true_positive_rapi': TP,
                'false_negative_rapi': FN,
                'false_positive_berantakan_as_rapi': FP,
                'true_negative_berantakan': TN
            }
        },
        'feature_importance': {
            col: float(imp) for col, imp in zip(X.columns, clf.feature_importances_)
        }
    }
    with open(EVAL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2)
    print(f"      Hasil evaluasi JSON disimpan di: {EVAL_JSON_PATH}")

    # Simpan Laporan Klasifikasi TXT
    with open(REPORT_SAVE_PATH, "w", encoding="utf-8") as f:
        f.write("====================================================================\n")
        f.write("        LAPORAN HASIL KLASIFIKASI MACHINE LEARNING (RANDOM FOREST)  \n")
        f.write("====================================================================\n\n")
        f.write("1. DATASET DAN KONFIGURASI MODEL:\n")
        f.write(f"   - File dataset utama     : {DATASET_CSV_PATH}\n")
        f.write(f"   - Total data             : 200 baris (14 fitur numerik + 1 label)\n")
        f.write(f"   - Algoritma              : Random Forest Classifier\n")
        f.write(f"   - Parameter Model        : n_estimators=100, random_state=14\n")
        f.write(f"   - Penggunaan Scaler      : Tidak digunakan (Random Forest invarian terhadap skala fitur)\n\n")
        
        f.write("2. PEMBAGIAN DATA DAN PENCEGAHAN DATA LEAKAGE:\n")
        f.write(f"   - Strategi Pembagian     : Stratified Group Split (Zero Data Leakage)\n")
        f.write(f"   - Alasan Penyesuaian Rasio:\n")
        f.write(f"     Terdapat 23 citra yang memiliki duplikasi exact (MD5) dan kemiripan visual tinggi\n")
        f.write(f"     (dHash jarak Hamming <= 5). Untuk mencegah data testing bocor ke data training,\n")
        f.write(f"     seluruh anggota grup duplikasi diisolasi ke satu partisi secara ketat.\n")
        f.write(f"   - Data Training          : {len(train_idx)} baris ({len(train_idx)/200*100:.1f}%) -> {dict(y_train.value_counts())}\n")
        f.write(f"   - Data Testing           : {len(test_idx)} baris ({len(test_idx)/200*100:.1f}%) -> {dict(y_test.value_counts())}\n")
        f.write(f"   - Overlapping Groups     : 0 grup (100% bebas kebocoran data)\n\n")
        
        f.write("3. HASIL EVALUASI MODEL PADA DATA TESTING:\n")
        f.write(f"   - Accuracy               : {acc:.4f} ({acc*100:.2f}%)\n")
        f.write(f"   - Precision (Macro Avg)  : {prec_macro:.4f}\n")
        f.write(f"   - Recall (Macro Avg)     : {rec_macro:.4f}\n")
        f.write(f"   - F1-Score (Macro Avg)   : {f1_macro:.4f}\n\n")
        
        f.write("4. CLASSIFICATION REPORT:\n")
        f.write(report_text)
        f.write("\n")
        
        f.write("5. CONFUSION MATRIX (Labels: ['rapi', 'berantakan']):\n")
        f.write(f"   Matrix:\n{cm}\n\n")
        f.write("   Interpretasi Komponen Confusion Matrix:\n")
        f.write(f"   * True Positive (TP)  : {TP} citra rapi benar diprediksi sebagai rapi.\n")
        f.write(f"   * False Negative (FN) : {FN} citra rapi salah diprediksi sebagai berantakan.\n")
        f.write(f"   * False Positive (FP) : {FP} citra berantakan salah diprediksi sebagai rapi.\n")
        f.write(f"   * True Negative (TN)  : {TN} citra berantakan benar diprediksi sebagai berantakan.\n\n")
        
        f.write("6. PERINGKAT PENGARUH FITUR (FEATURE IMPORTANCE TOP 5):\n")
        sorted_feats = sorted(zip(X.columns, clf.feature_importances_), key=lambda x: x[1], reverse=True)
        for rank, (feat_name, val) in enumerate(sorted_feats, 1):
            f.write(f"   {rank:2d}. {feat_name:12s}: {val:.4f} ({val*100:.2f}%)\n")
        f.write("\n")
        
        f.write("7. LOKASI FILE ARTIFAK:\n")
        f.write(f"   - Model Terlatih         : {MODEL_SAVE_PATH}\n")
        f.write(f"   - Visual Confusion Matrix: {CM_IMAGE_PATH}\n")
        f.write(f"   - Visual Feature Import. : {FEAT_IMP_IMAGE_PATH}\n")
        f.write(f"   - Evaluasi JSON Lengkap  : {EVAL_JSON_PATH}\n")
        f.write(f"   - Laporan Teks           : {REPORT_SAVE_PATH}\n")
        
    print(f"      Laporan teks klasifikasi disimpan di: {REPORT_SAVE_PATH}")
    return eval_data

if __name__ == '__main__':
    res = run_classification()
    print("\n" + "="*50)
    print("HASIL AKHIR KLASIFIKASI RANDOM FOREST")
    print("="*50)
    m = res['metrics']
    print(f"Akurasi Model : {m['accuracy_percentage']}")
    print(f"Macro Prec    : {m['macro_avg']['precision']:.4f}")
    print(f"Macro Recall  : {m['macro_avg']['recall']:.4f}")
    print(f"Macro F1      : {m['macro_avg']['f1_score']:.4f}")
    print("\nConfusion Matrix [rapi, berantakan]:")
    print(np.array(m['confusion_matrix']['matrix']))
    print(f"TP: {m['confusion_matrix']['true_positive_rapi']}, FN: {m['confusion_matrix']['false_negative_rapi']}")
    print(f"FP: {m['confusion_matrix']['false_positive_berantakan_as_rapi']}, TN: {m['confusion_matrix']['true_negative_berantakan']}")

