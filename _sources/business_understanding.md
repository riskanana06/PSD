# Business Understanding

Tahap awal dalam metodologi *Cross-Industry Standard Process for Data Mining* (CRISP-DM) berfokus pada pemahaman tujuan proyek dari sudut pandang kebutuhan analisis atau domain masalah, kemudian menerjemahkannya ke dalam definisi masalah sains data.

---

## 1. Latar Belakang Masalah

Pertumbuhan aktivitas industri, transportasi, dan pola mobilitas perkotaan memberikan dampak langsung terhadap dinamika lingkungan, khususnya penurunan kualitas udara. Parameter polutan seperti karbon monoksida (CO), nitrogen dioksida ($\text{NO}_2$), sulfur dioksida ($\text{SO}_2$), dan ozon ($\text{O}_3$) kerap berfluktuasi seiring waktu. 

Tanpa pemantauan dan analisis berbasis data, identifikasi pola kenaikan polutan menjadi lambat, sehingga upaya mitigasi risiko kesehatan masyarakat menjadi kurang efektif. Oleh karena itu, diperlukan eksplorasi data historis dan pemodelan prediktif untuk memetakan tren serta karakteristik pencemaran.

---

## 2. Tujuan Analisis (*Objectives*)

Tujuan utama dari proyek sains data ini meliputi:

* **Eksplorasi Data:** Mengidentifikasi sebaran temporal dan pola fluktuasi konsentrasi polutan udara di wilayah amatan.
* **Analisis Korelasi:** Menemukan keterkaitan dan dependensi antarfaktor polutan untuk memahami parameter yang paling dominan.
* **Pemodelan & Prediksi:** Membangun model *machine learning* untuk mengklasifikasikan atau memprediksi kategori indeks standar pencemar udara secara akurat.

---

## 3. Rumusan Masalah

Berdasarkan latar belakang tersebut, rumusan masalah yang diselesaikan adalah:

1. Bagaimana tren konsentrasi polutan utama pada rentang waktu pengamatan?
2. Parameter apa saja yang memiliki kontribusi signifikan terhadap lonjakan tingkat polusi?
3. Seberapa baik model analitik mampu mengklasifikasikan atau memprediksi tingkat kualitas udara berdasarkan metrik evaluasi?

---

## 4. Tolak Ukur Keberhasilan (*Success Criteria*)

Keberhasilan proyek ini diukur berdasarkan dua aspek:

| Aspek | Kriteria Keberhasilan |
| :--- | :--- |
| **Kebutuhan Analisis** | Dihasilkannya wawasan kuantitatif mengenai pola waktu dan korelasi polutan yang dapat dijadikan rujukan mitigasi lingkungan. |
| **Teknis Sains Data** | Model *machine learning* mencapai performa stabil dengan metrik evaluasi (seperti *Accuracy*, *Precision*, atau *Recall*) di atas batas minimum yang ditentukan. |

---

## 5. Rencana Proyek (*Project Plan*)

Alur kerja proyek sains data terbagi ke dalam tahapan berurutan:

* **Pengumpulan & Ekstraksi Data:** Mengambil data deret waktu polutan atau atribut terkait dari sumber resmi.
* **Pembersihan Data (*Data Preparation*):** Menangani nilai kosong (*missing values*), normalisasi fitur, dan pembagian dataset (*train-test split*).
* **Pemodelan (*Modeling*):** Menerapkan algoritma klasifikasi/regresi yang sesuai dengan karakteristik data.
* **Evaluasi (*Evaluation*):** Menguji ketahanan model menggunakan matriks evaluasi dan visualisasi performa.