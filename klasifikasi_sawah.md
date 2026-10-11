# Klasifikasi Lahan Jawa Timur

## Alur Penelitian

Mulai → Menentukan tujuan dan 6 kelas lahan → Membuat polygon sampel → Mengambil citra Sentinel-2A → Menyaring piksel berawan/tidak valid → Menghitung 13 fitur → Membagi data training dan testing berdasarkan polygon → Membandingkan 3 model menggunakan validasi → Memilih model terbaik → Menguji model pada data testing → Menampilkan peta hasil klasifikasi → Analisis kebijakan penggunaan lahan → Selesai.

## 1. Tujuan Analisis

Analisis ini bertujuan mengklasifikasikan lokasi sampel lahan di Jawa Timur menjadi enam kelas, yaitu sawah, bangunan, mangrove, lahan hijau, laut, dan danau.

Analisis penggunaan lahan (*land use*) membantu memahami pemanfaatan suatu wilayah, misalnya untuk pertanian dan kawasan terbangun. Klasifikasi penutup lahan (*land cover classification*) membantu membedakan karakteristik permukaan berdasarkan informasi citra satelit.

Hasil klasifikasi dapat menjadi bahan awal untuk kajian pemanfaatan ruang, perlindungan kawasan pertanian, pelestarian mangrove, serta pengamatan badan air. Penetapan kesesuaian terhadap kebijakan tata ruang memerlukan data kebijakan dan batas kawasan yang relevan.

## 2. Data Understanding

### 2.1 Wilayah dan Kelas

Lokasi sampel berada di wilayah kajian Jawa Timur. Data sampel disimpan dalam file `PSD_6_Kelas_Gabungan.geojson`.

Setiap polygon memiliki `sample_id` sebagai identitas dan `kelas` sebagai label acuan.

| Kelas | Pengertian dalam penelitian | Jumlah Polygon |
|---|---|---:|
| Sawah | Lahan pertanian sawah | 30 |
| Bangunan | Kawasan dengan penutup berupa bangunan atau permukaan terbangun | 30 |
| Mangrove | Vegetasi mangrove di kawasan pesisir | 30 |
| Lahan Hijau | Vegetasi selain sampel sawah dan mangrove | 30 |
| Laut | Perairan laut terbuka | 30 |
| Danau | Badan air danau atau ranu | 30 |
| **Total** | **Enam kelas** | **180** |

Lahan hijau merupakan kelompok umum dalam eksperimen ini. Kelas tersebut belum dipecah menjadi hutan, semak, kebun, atau jenis vegetasi lainnya.

### 2.2 Acuan Klasifikasi Lahan di Indonesia

Acuan standar yang digunakan untuk pembahasan klasifikasi penutup lahan adalah **SNI 7645-1:2014, Klasifikasi penutup lahan — Bagian 1: Skala kecil dan menengah**, yang diterbitkan Badan Standardisasi Nasional.

Enam kelas pada penelitian ini merupakan pengelompokan operasional sesuai kebutuhan tugas. Pengelompokan ini bukan salinan lengkap seluruh kelas dan hierarki SNI.

### 2.3 Sumber Citra

Citra yang digunakan adalah **Sentinel-2A Level-2A** dari Copernicus Data Space Ecosystem.

Periode pencarian citra adalah **1 Juni sampai 30 September 2026**. Untuk setiap lokasi sampel, pencarian dilakukan berdasarkan lokasi polygon dan ketersediaan citra.

Citra dipilih dengan mempertimbangkan persentase awan pada tile. Setelah diunduh, kualitas piksel di dalam polygon diperiksa kembali. Persentase awan pada tile tidak selalu sama dengan kondisi awan pada lokasi sampel.

Tanggal citra dapat berbeda antarpolygon. Identitas citra dan tanggal pengambilan disimpan dalam metadata masing-masing sampel.

## 3. Pengumpulan Data

Pengumpulan data dilakukan melalui langkah berikut:

1. Membaca GeoJSON yang berisi 180 polygon berlabel.
2. Mencari citra Sentinel-2A Level-2A pada periode penelitian.
3. Mengunduh band citra menggunakan Process API.
4. Menyimpan citra setiap sampel dalam format TIFF.
5. Menyimpan metadata citra dalam format JSON.
6. Membuat laporan status pengunduhan.

Folder penyimpanan citra adalah `citra_sentinel`.

Setiap TIFF memiliki 12 layer, yaitu 10 band reflektansi, satu layer SCL, dan satu layer dataMask.

Seluruh **180 sampel** berhasil tersedia setelah proses pengunduhan selesai.

## 4. Band Sentinel-2A

Sentinel-2 memiliki 13 band spektral dengan resolusi spasial asli yang berbeda.

| Band | Jenis Spektral | Resolusi Asli | Keterangan |
|---|---|---:|---|
| B01 | Coastal aerosol | 60 m | Informasi aerosol dan wilayah pesisir |
| B02 | Blue | 10 m | Pantulan pada spektrum biru |
| B03 | Green | 10 m | Pantulan pada spektrum hijau |
| B04 | Red | 10 m | Pantulan merah untuk analisis vegetasi |
| B05 | Red edge 1 | 20 m | Karakteristik vegetasi |
| B06 | Red edge 2 | 20 m | Karakteristik vegetasi |
| B07 | Red edge 3 | 20 m | Karakteristik vegetasi |
| B08 | Near infrared | 10 m | Pantulan inframerah dekat |
| B8A | Narrow near infrared | 20 m | Inframerah dekat dengan rentang lebih sempit |
| B09 | Water vapour | 60 m | Informasi uap air atmosfer |
| B10 | Cirrus | 60 m | Deteksi cirrus; tidak tersedia sebagai band reflektansi permukaan pada produk Level-2A |
| B11 | Shortwave infrared 1 | 20 m | Karakteristik kelembapan dan permukaan |
| B12 | Shortwave infrared 2 | 20 m | Karakteristik kelembapan dan permukaan |

Band reflektansi yang digunakan sebagai fitur adalah `B02`, `B03`, `B04`, `B05`, `B06`, `B07`, `B08`, `B8A`, `B11`, dan `B12`.

Citra diunduh pada grid 10 meter dalam koordinat UTM. Band yang memiliki resolusi asli 20 meter diresampling ke grid tersebut. Resampling tidak menambah detail spasial asli band.

Dua layer tambahan digunakan untuk pemeriksaan kualitas:

| Layer | Fungsi |
|---|---|
| SCL | Scene Classification Layer untuk menyaring kelas kualitas piksel |
| dataMask | Menunjukkan ketersediaan data pada piksel |

SCL dan dataMask digunakan untuk penyaringan, bukan sebagai fitur model.

## 5. Penyaringan Piksel

Piksel yang digunakan harus memenuhi kondisi berikut:

- Berada di dalam polygon sampel.
- Memiliki `dataMask = 1`.
- Memiliki nilai band dan fitur yang valid.
- Tidak termasuk kelas SCL yang dikeluarkan.

Kelas SCL yang dikeluarkan adalah `0`, `1`, `3`, `8`, `9`, `10`, dan `11`, yang mencakup no data, piksel rusak atau jenuh, bayangan awan, awan, cirrus, serta salju atau es.

Setiap polygon diambil maksimal **500 piksel bersih**. Jumlah piksel dapat lebih sedikit karena ukuran polygon dan ketersediaan piksel valid.

## 6. Ekstraksi Fitur

Model menggunakan **13 fitur per piksel**, yaitu 10 band reflektansi dan tiga indeks spektral.

| Fitur | Keterangan |
|---|---|
| B02 | Reflektansi band biru |
| B03 | Reflektansi band hijau |
| B04 | Reflektansi band merah |
| B05 | Reflektansi red edge 1 |
| B06 | Reflektansi red edge 2 |
| B07 | Reflektansi red edge 3 |
| B08 | Reflektansi inframerah dekat |
| B8A | Reflektansi inframerah dekat sempit |
| B11 | Reflektansi SWIR 1 |
| B12 | Reflektansi SWIR 2 |
| NDVI | Indeks vegetasi |
| NDWI | Indeks air |
| NDBI | Indeks yang membantu mengenali kawasan terbangun |

### 6.1 NDVI

NDVI (*Normalized Difference Vegetation Index*) menggunakan band inframerah dekat dan merah.

$$
NDVI = \frac{B08-B04}{B08+B04}
$$

NDVI membantu membedakan karakteristik vegetasi.

### 6.2 NDWI

NDWI (*Normalized Difference Water Index*) pada penelitian ini menggunakan band hijau dan inframerah dekat.

$$
NDWI = \frac{B03-B08}{B03+B08}
$$

NDWI membantu mengenali badan air.

### 6.3 NDBI

NDBI (*Normalized Difference Built-up Index*) menggunakan band SWIR dan inframerah dekat.

$$
NDBI = \frac{B11-B08}{B11+B08}
$$

NDBI membantu membedakan kawasan terbangun. Nilainya juga dapat dipengaruhi tanah terbuka, sehingga tidak digunakan sebagai penentu kelas secara tunggal.

Penyebut yang mendekati nol menghasilkan nilai tidak valid dan dikeluarkan sebelum pemodelan.

### 6.4 Ringkasan Fitur per Polygon

Selain dataset piksel, ekstraksi menghasilkan ringkasan mean, median, dan standar deviasi setiap fitur per polygon.

Ringkasan dihitung dari seluruh piksel valid sebelum pembatasan maksimal 500 piksel.

Mean:

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i
$$

Median merupakan nilai tengah setelah data diurutkan. Jika jumlah data genap, median adalah rata-rata dua nilai tengah.

Standar deviasi yang digunakan memakai pembagi $n$:

$$
\sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2}
$$

Keterangan:

- $x_i$ adalah nilai fitur pada piksel ke-$i$.
- $n$ adalah jumlah piksel valid.
- $\bar{x}$ adalah rata-rata nilai fitur.
- $\sigma$ adalah standar deviasi.

Ringkasan tersebut disimpan dalam `fitur_polygon_sentinel.csv`. Model dalam eksperimen ini dilatih menggunakan 13 fitur per piksel, bukan ringkasan statistik polygon.

## 7. Hasil Ekstraksi

Seluruh **180 polygon** berhasil diekstraksi.

| Kelas | Jumlah Polygon | Jumlah Piksel Diambil |
|---|---:|---:|
| Sawah | 30 | 9.927 |
| Bangunan | 30 | 4.685 |
| Mangrove | 30 | 9.509 |
| Lahan Hijau | 30 | 6.160 |
| Laut | 30 | 2.983 |
| Danau | 30 | 8.353 |
| **Total** | **180** | **41.617** |

Jumlah fitur per piksel adalah **13**. Dataset hasil ekstraksi memiliki **0 missing value pada fitur**.

Jumlah polygon tiap kelas seimbang, tetapi jumlah piksel berbeda. Perbedaan dipengaruhi ukuran polygon dan jumlah piksel yang lolos penyaringan.

## 8. Pembagian Training dan Testing

Pembagian dilakukan pada tingkat polygon dengan proporsi **80% training** dan **20% testing**, menggunakan stratifikasi kelas dan `random_state = 42`.

Seluruh piksel dari satu polygon masuk ke kelompok yang sama.

| Kelas | Total Polygon | Training | Testing |
|---|---:|---:|---:|
| Sawah | 30 | 24 | 6 |
| Bangunan | 30 | 24 | 6 |
| Mangrove | 30 | 24 | 6 |
| Lahan Hijau | 30 | 24 | 6 |
| Laut | 30 | 24 | 6 |
| Danau | 30 | 24 | 6 |
| **Total** | **180** | **144** | **36** |

| Kelompok | Jumlah Polygon | Jumlah Piksel |
|---|---:|---:|
| Training | 144 | 33.440 |
| Testing | 36 | 8.177 |
| **Total** | **180** | **41.617** |

Polygon digunakan sebagai unit pembagian data, sedangkan piksel digunakan sebagai baris input model.

Pembagian ini mencegah piksel dari polygon yang sama masuk ke training dan testing. Namun, pembagian berdasarkan identitas polygon belum menjamin lokasi training dan testing berjauhan secara spasial.

## 9. Eksperimen Model

Tiga model dibandingkan:

1. Random Forest.
2. Extra Trees.
3. Hist Gradient Boosting.

Random Forest dan Extra Trees menggunakan 200 pohon. Jumlah pohon merupakan pengaturan model, bukan jumlah sampel.

Extra Trees adalah gabungan banyak pohon keputusan dengan pemilihan pemisahan yang diacak. Karena itu, Extra Trees berbeda dari satu Decision Tree.

Validasi silang dilakukan dalam tiga fold pada **144 polygon training**. Pembagian fold dilakukan berdasarkan polygon, lalu piksel mengikuti kelompok polygonnya.

Pada pelatihan, bobot piksel diatur agar setiap polygon memiliki total bobot yang sama.

Prediksi polygon ditentukan dari rata-rata probabilitas kelas seluruh piksel sampelnya:

$$
\bar{p}_{g,c} = \frac{1}{n_g}\sum_{i=1}^{n_g}p_{i,c}
$$

$$
\hat{y}_g = \operatorname{argmax}_{c}\bar{p}_{g,c}
$$

Keterangan:

- $g$ adalah polygon.
- $c$ adalah kelas.
- $n_g$ adalah jumlah piksel sampel pada polygon.
- $p_{i,c}$ adalah probabilitas kelas $c$ untuk piksel $i$.
- $\hat{y}_g$ adalah kelas prediksi polygon.

## 10. Perbandingan Model

Hasil berikut merupakan evaluasi validasi silang pada data training.

| Model | Rata-rata Accuracy Polygon | Standar Deviasi Accuracy | Macro F1 Polygon | Accuracy Piksel |
|---|---:|---:|---:|---:|
| Extra Trees | 79,86% | 4,34 poin persentase | 0,796857 | 75,00% |
| Random Forest | 79,86% | 4,34 poin persentase | 0,796596 | 75,08% |
| Hist Gradient Boosting | 78,47% | 2,41 poin persentase | 0,782172 | 74,51% |

Extra Trees dan Random Forest memperoleh rata-rata accuracy polygon yang sama. **Extra Trees dipilih karena macro F1 polygon sedikit lebih tinggi.**

Model terpilih kemudian dilatih ulang menggunakan seluruh data training dan dievaluasi pada data testing.

Pemilihan dilakukan berdasarkan hasil validasi training. Extra Trees merupakan model terbaik di antara konfigurasi yang dicoba dengan kriteria pemilihan tersebut.

## 11. Hasil Testing

### 11.1 Evaluasi Polygon

Model Extra Trees memperoleh hasil berikut pada 36 polygon testing:

| Metrik | Hasil |
|---|---:|
| Accuracy polygon | 83,33% |
| Macro F1 polygon | 0,8302 |
| Polygon benar | 30 |
| Polygon salah | 6 |

Rumus accuracy:

$$
Accuracy = \frac{\text{Jumlah prediksi benar}}{\text{Jumlah sampel uji}}
$$

Dalam persen:

$$
Accuracy = \frac{30}{36}\times100\% = 83{,}33\%
$$

### 11.2 Evaluasi Piksel

| Metrik | Hasil |
|---|---:|
| Jumlah piksel testing | 8.177 |
| Accuracy piksel | 81,67% |
| Balanced accuracy piksel | 77,24% |
| Macro F1 piksel | 0,7921 |

Precision dan recall dihitung sebagai:

$$
Precision = \frac{TP}{TP+FP}
$$

$$
Recall = \frac{TP}{TP+FN}
$$

$$
F1 = \frac{2\times Precision\times Recall}{Precision+Recall}
$$

Keterangan untuk setiap kelas:

- $TP$: sampel kelas tersebut yang diprediksi dengan benar.
- $FP$: sampel kelas lain yang diprediksi sebagai kelas tersebut.
- $FN$: sampel kelas tersebut yang diprediksi sebagai kelas lain.

Macro F1 adalah rata-rata F1 seluruh kelas tanpa pembobotan jumlah sampel:

$$
Macro\ F1 = \frac{1}{K}\sum_{c=1}^{K}F1_c
$$

Balanced accuracy adalah rata-rata recall seluruh kelas:

$$
Balanced\ Accuracy = \frac{1}{K}\sum_{c=1}^{K}Recall_c
$$

Pada penelitian ini, $K=6$.

Accuracy piksel dan accuracy polygon dihitung pada unit yang berbeda sehingga nilainya dapat berbeda.

### 11.3 Confusion Matrix Polygon

```{figure} _static/confusion_matrix_polygon.png
---
width: 90%
name: confusion-matrix-polygon
---
Confusion matrix model Extra Trees pada 36 polygon testing.
```

Baris menunjukkan kelas acuan, sedangkan kolom menunjukkan kelas prediksi.

Angka pada diagonal menunjukkan prediksi benar. Angka di luar diagonal menunjukkan kesalahan klasifikasi.

Sebanyak **30 dari 36 polygon testing** diprediksi dengan benar, sedangkan **enam polygon** diprediksi sebagai kelas lain.

### 11.4 Confusion Matrix Piksel

```{figure} _static/confusion_matrix_piksel.png
---
width: 90%
name: confusion-matrix-piksel
---
Confusion matrix model Extra Trees pada 8.177 piksel testing.
```

Evaluasi ini dihitung pada tingkat piksel. Accuracy piksel sebesar **81,67%**, balanced accuracy sebesar **77,24%**, dan macro F1 sebesar **0,7921**.

### 12.1 Analisis Hasil Klasifikasi terhadap Kebijakan Penggunaan Lahan

Hasil klasifikasi menunjukkan 30 polygon diprediksi sebagai sawah, 32 bangunan, 32 mangrove, 28 lahan hijau, 28 laut, dan 30 danau. Hasil ini digunakan untuk membahas kaitan karakteristik penutup lahan dengan kebijakan penggunaan ruang di Jawa Timur.

Acuan tata ruang wilayah kajian adalah **Peraturan Daerah Provinsi Jawa Timur Nomor 10 Tahun 2023 tentang Rencana Tata Ruang Wilayah Provinsi Jawa Timur Tahun 2023–2043**.

Kelas hasil klasifikasi menggambarkan karakteristik permukaan pada lokasi sampel. Sementara itu, kebijakan tata ruang mengatur peruntukan ruang. Oleh karena itu, kelas hasil prediksi perlu dibandingkan dengan peta kebijakan sebelum digunakan untuk menilai kesesuaian pemanfaatan suatu lokasi.

#### A. Sawah dan Perlindungan Lahan Pertanian

Model memprediksi 30 polygon sebagai sawah. Kelas sawah berkaitan dengan **Undang-Undang Nomor 41 Tahun 2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan beserta perubahannya**.

Identifikasi sawah dapat membantu menyediakan informasi awal tentang lokasi lahan pertanian yang perlu diperiksa dalam pembahasan perlindungan lahan pangan.

Namun, polygon yang diprediksi sebagai sawah belum otomatis merupakan Lahan Pertanian Pangan Berkelanjutan atau LP2B. Status tersebut memerlukan data penetapan resmi.

Jumlah prediksi sawah yang sama dengan jumlah label acuan juga tidak berarti semua polygon sawah diprediksi dengan benar. Kesalahan antar kelas dapat saling mengimbangi jumlahnya. Penilaian ketepatan tetap mengacu pada hasil testing dan confusion matrix.

#### B. Bangunan dan Pemanfaatan Ruang

Model memprediksi 32 polygon sebagai bangunan, sedangkan label acuan bangunan berjumlah 30 polygon. Selisih tersebut menunjukkan perbedaan hasil model terhadap label acuan pada kumpulan sampel.

Selisih dua polygon ini tidak membuktikan adanya pembangunan baru atau alih fungsi lahan. Analisis perubahan membutuhkan pengamatan lokasi yang sama pada waktu berbeda.

Dalam kaitannya dengan RTRW, identifikasi kawasan terbangun dapat menjadi bahan awal untuk membandingkan kondisi permukaan dengan peruntukan ruang. Penilaian kesesuaian membutuhkan peta pola ruang dan ketentuan yang berlaku pada lokasi tersebut.

Hasil klasifikasi bangunan saja belum dapat menentukan apakah suatu pembangunan sesuai atau melanggar kebijakan tata ruang.

#### C. Mangrove dan Perlindungan Ekosistem Pesisir

Model memprediksi 32 polygon sebagai mangrove. Kelas ini berkaitan dengan **Peraturan Pemerintah Nomor 27 Tahun 2025 tentang Perlindungan dan Pengelolaan Ekosistem Mangrove**.

Pemetaan mangrove dapat membantu mengidentifikasi lokasi vegetasi pesisir sebagai bahan awal inventarisasi dan pemeriksaan kondisi ekosistem.

Jumlah prediksi mangrove yang lebih tinggi dari label acuan belum menunjukkan peningkatan luas mangrove. Data yang dihitung merupakan jumlah polygon sampel, bukan luas seluruh ekosistem.

Untuk pembahasan perlindungan mangrove pada lokasi tertentu, hasil prediksi perlu diverifikasi dan dibandingkan dengan data resmi ekosistem serta fungsi kawasan.

#### D. Lahan Hijau dan Kawasan Vegetasi

Model memprediksi 28 polygon sebagai lahan hijau. Kelas ini menggabungkan vegetasi selain sawah dan mangrove sehingga belum membedakan hutan, kebun, semak, atau ruang terbuka hijau.

Pengelompokan tersebut berguna untuk mengenali permukaan bervegetasi, tetapi belum cukup untuk menetapkan fungsi kawasan berdasarkan kebijakan.

Polygon lahan hijau tidak otomatis merupakan kawasan lindung atau ruang terbuka hijau resmi. Penilaian tersebut membutuhkan klasifikasi vegetasi yang lebih rinci dan peta peruntukan ruang.

#### E. Laut, Danau, dan Perlindungan Badan Air

Model memprediksi 28 polygon sebagai laut dan 30 polygon sebagai danau. Pemisahan dua kelas ini membantu membedakan sampel perairan pesisir dan perairan daratan.

Untuk danau, acuan yang relevan adalah **Peraturan Menteri PUPR Nomor 28/PRT/M/2015 tentang Penetapan Garis Sempadan Sungai dan Garis Sempadan Danau**.

Identifikasi badan air dapat menjadi informasi awal dalam pembahasan perlindungan danau. Namun, polygon sampel danau belum menunjukkan keseluruhan batas danau maupun garis sempadan resminya.

Untuk laut, hasil klasifikasi menunjukkan karakteristik penutup berupa perairan. Hasil tersebut belum menentukan zonasi atau kegiatan yang diizinkan pada ruang laut.

#### F. Ketelitian Hasil dan Batas Analisis Kebijakan

Pada 36 polygon testing, sebanyak 30 polygon diprediksi dengan benar dan enam polygon salah. Accuracy polygon sebesar 83,33% menunjukkan bahwa hasil model masih memiliki kesalahan.

Enam kesalahan testing ditandai pada peta agar lokasi yang memerlukan pemeriksaan dapat dikenali. Lokasi dengan prediksi yang berbeda dari label acuan perlu diverifikasi sebelum hasilnya digunakan untuk pembahasan kebijakan.

Jumlah polygon setiap kelas tidak menunjukkan persentase luas penutup lahan Jawa Timur. Sampel berjumlah 180 polygon dengan jumlah label acuan yang sengaja diseimbangkan, yaitu 30 polygon setiap kelas.

Penelitian ini belum melakukan overlay hasil klasifikasi dengan peta RTRW, RDTR, LP2B, fungsi ekosistem mangrove, atau sempadan danau. Karena itu, analisis yang disajikan merupakan interpretasi hubungan hasil klasifikasi dengan kebijakan, bukan penetapan kepatuhan hukum pada masing-masing lokasi.

### 12.2 Sumber Kebijakan

- Pemerintah Provinsi Jawa Timur. [Perda Nomor 10 Tahun 2023 tentang RTRW Provinsi Jawa Timur Tahun 2023–2043](https://jdih.jatimprov.go.id/site-pages/dokumen-populer/peraturan-daerah-provinsi-jawa-timur-nomor-10-tahun-2023-tentang-rencana-tata-ruang-wilayah-provinsi-jawa-timur-tahun-2023-2043).
- Pemerintah Republik Indonesia. [UU Nomor 41 Tahun 2009 tentang Perlindungan Lahan Pertanian Pangan Berkelanjutan](https://jdih.pertanian.go.id/peraturan/uu-nomor-41-tahun-2009), beserta perubahannya.
- Pemerintah Republik Indonesia. [PP Nomor 27 Tahun 2025 tentang Perlindungan dan Pengelolaan Ekosistem Mangrove](https://jdih.kemenkopangan.go.id/peraturan-pemerintah-nomor-27-tahun-2025-tentang-perlindungan-dan-pengelolaan-ekosistem-mangrove).
- Kementerian PUPR. [Permen PUPR Nomor 28/PRT/M/2015 tentang Penetapan Garis Sempadan Sungai dan Garis Sempadan Danau](https://peraturan.go.id/id/permen-pupr-no-28-prt-m-2015-tahun-2015).

## 13. File dan Kode Pengolahan

| File | Fungsi |
|---|---|
| PSD_6_Kelas_Gabungan.geojson | Polygon dan label acuan |
| unduh_sentinel_semua.py | Pengunduhan citra setiap sampel |
| ekstraksi_fitur_sentinel.py | Penyaringan piksel dan ekstraksi fitur |
| klasifikasi_sentinel.py | Pembagian data, eksperimen model, dan evaluasi |
| buat_peta_hasil.py | Pembuatan peta hasil prediksi |
| app.py | Aplikasi sistem informasi klasifikasi lahan di Streamlit |
| requirements.txt | Daftar paket Python yang diperlukan aplikasi |
| hasil_ekstraksi/dataset_piksel_sentinel.csv | Dataset 13 fitur per piksel |
| hasil_ekstraksi/fitur_polygon_sentinel.csv | Ringkasan statistik fitur per polygon |
| hasil_klasifikasi/perbandingan_model.csv | Hasil perbandingan model |
| hasil_klasifikasi/prediksi_peta_polygon.csv | Prediksi dan pembagian data pada 180 polygon |
| hasil_klasifikasi/hasil_prediksi_polygon.geojson | Geometri polygon beserta hasil prediksi untuk peta |
| hasil_klasifikasi/hasil_evaluasi.json | Ringkasan evaluasi |
| hasil_klasifikasi/model_terbaik.joblib | Model terpilih dan informasi fitur |
| _static/confusion_matrix_polygon.png | Gambar evaluasi polygon |
| _static/confusion_matrix_piksel.png | Gambar evaluasi piksel |
| _static/peta_klasifikasi_sentinel.html | Peta interaktif pada web statis |

Kode pengolahan dijalankan di VS Code. Halaman web statis menyajikan proses dan hasil yang sudah diperoleh.

## 14. Deployment Sistem Informasi

Sistem informasi klasifikasi lahan dibuat menggunakan **Streamlit** dan dideploy melalui **Streamlit Community Cloud**.

[Buka aplikasi klasifikasi lahan di Streamlit](https://riska-klasifikasi-lahan-jatim.streamlit.app/)

Aplikasi menyediakan empat tab:

| Tab | Isi |
|---|---|
| Eksplorasi Data | Jumlah polygon per kelas, distribusi kelas, jumlah piksel, contoh dataset, missing value, serta statistik fitur |
| Peta Spasial | Peta hasil klasifikasi menggunakan Folium/Leaflet dengan latar Google Hybrid dan pilihan Esri Satellite |
| Model Extra Trees | Pembagian training/testing, perbandingan model, metrik evaluasi, dan confusion matrix |
| Prediksi Data Baru | Form input reflektansi 10 band Sentinel-2A untuk menghasilkan prediksi kelas lahan |

Filter kelas pada sidebar berlaku untuk hasil prediksi di tab **Peta Spasial**.

Aplikasi memuat model Extra Trees yang telah dilatih dari `model_terbaik.joblib`. Model dipilih berdasarkan validasi silang pada data training, kemudian dievaluasi pada data testing.

Pada tab **Prediksi Data Baru**, pengguna memasukkan nilai reflektansi 10 band. Aplikasi menghitung NDVI, NDWI, dan NDBI secara otomatis sehingga input model tetap terdiri dari 13 fitur.

Nilai awal form merupakan median fitur dataset sebagai contoh pengisian. Untuk memprediksi citra baru, nilai tersebut diganti dengan reflektansi piksel citra yang ingin dianalisis.

Hasil form berupa prediksi satu piksel dan probabilitas untuk setiap kelas. Probabilitas tersebut berbeda dari accuracy testing. Prediksi polygon pada peta menggunakan rata-rata probabilitas piksel sampel di dalam polygon.

**Web statis Jupyter Book** memuat dokumentasi pengumpulan data, data understanding, band Sentinel-2A, preprocessing, ekstraksi fitur, pembagian data, eksperimen model, evaluasi, dan peta.

[Buka web statis PSD](https://riskanana06.github.io/PSD/)

Web statis memuat proses penelitian dan link aplikasi Streamlit. Aplikasi Streamlit menjalankan sistem informasi interaktif secara terpisah.

## 15. Referensi

- Badan Standardisasi Nasional. SNI 7645-1:2014, Klasifikasi penutup lahan — Bagian 1: Skala kecil dan menengah. [Katalog BSN](https://pesta.bsn.go.id/produk/by_ics/5?ics_no=07&key=).
- Copernicus Data Space Ecosystem. [Sentinel-2 Level-2A](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html).
- Copernicus Data Space Ecosystem. [Sentinel-2 Level-1C](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L1C.html).
- Scikit-learn. [Ensemble methods](https://scikit-learn.org/1.6/modules/ensemble.html).