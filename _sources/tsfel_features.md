---

## 3. Rincian dan Nilai Fitur Berdasarkan Domain

Hasil ekstraksi fitur dari file `NO2_AsemRowo_TSFEL_68.csv` dikelompokkan ke dalam tiga domain utama:

---

### A. Domain Statistik (Statistical Features)

Domain ini mengukur karakteristik distribusi probabilitas, pemusatan nilai, serta variabilitas konsentrasi $\text{NO}_2$ tanpa memperhitungkan urutan waktu.

| No | Nama Fitur | Deskripsi Matematis & Fisis | Nilai Fitur |
| :---: | :--- | :--- | :--- |
| 1 | `0_Absolute energy` | Total energi sinyal melalui penjumlahan kuadrat semua nilai data. | $1,02 \times 10^{-6}$ |
| 2 | `0_Average power` | Rata-rata daya sinyal per hari (energi absolut dibagi total sampel). | $2,78 \times 10^{-9}$ |
| 3 | `0_Kurtosis` | Derajat keruncingan distribusi data terhadap kurva normal. | $0,8452$ |
| 4 | `0_Maximum` | Nilai konsentrasi tertinggi $\text{NO}_2$ selama 366 hari pengamatan. | $0,000101$ |
| 5 | `0_Mean` | Rata-rata aritmatika tingkat polusi harian di Asem Rowo. | $0,000049$ |
| 6 | `0_Mean absolute deviation` | Rata-rata jarak absolut setiap observasi terhadap titik mean. | $0,000014$ |
| 7 | `0_Median` | Nilai tengah dari seluruh urutan data konsentrasi polutan. | $0,000047$ |
| 8 | `0_Median absolute deviation` | Median selisih mutlak observasi dari median data (ukuran dispersi robust). | $0,000011$ |
| 9 | `0_Minimum` | Konsentrasi polutan terendah yang terdeteksi. | $0,000012$ |
| 10 | `0_Root mean square (RMS)` | Akar kuadrat dari rata-rata kuadrat nilai sinyal. | $0,000053$ |
| 11 | `0_Skewness` | Derajat ketidaksimetrisan (kemencengan) distribusi terhadap rata-rata. | $0,4128$ |
| 12 | `0_Standard deviation` | Variabilitas atau persebaran nilai observasi di sekitar rata-rata. | $0,000018$ |
| 13 | `0_Variance` | Kuadrat standar deviasi yang menunjukkan sebaran variansi data. | $3,24 \times 10^{-10}$ |
| 14 | `0_Interquartile range (IQR)` | Rentang rentang antara persentil ke-75 ($Q_3$) dan persentil ke-25 ($Q_1$). | $0,000025$ |
| 15 | `0_Histogram Mode` | Titik bin frekuensi yang paling sering muncul pada kurva kepadatan. | $0,000044$ |

---

### B. Domain Temporal (Temporal Features)

Domain temporal mengukur struktur keterurutan waktu, persistensi perubahan harian, serta kestabilan pergerakan deret polutan.

| No | Nama Fitur | Deskripsi Matematis & Fisis | Nilai Fitur |
| :---: | :--- | :--- | :--- |
| 1 | `0_Autocorrelation` | Korelasi sinyal dengan versi dirinya sendiri pada pergeseran lag tertentu. | $0,8912$ |
| 2 | `0_Centroid` | Pusat massa temporal dari distribusi energi sinyal sepanjang tahun. | $183,42$ |
| 3 | `0_Mean absolute differences` | Rata-rata perubahan absolut nilai polutan dari satu hari ke hari berikutnya. | $0,000008$ |
| 4 | `0_Mean differences` | Rata-rata selisih terarah harian (mengukur tren akumulasi). | $-1,12 \times 10^{-8}$ |
| 5 | `0_Median absolute differences` | Median perubahan harian yang tahan terhadap lonjakan ekstrem singkat. | $0,000006$ |
| 6 | `0_Median differences` | Median selisih terarah antarhari berurutan. | $0,000000$ |
| 7 | `0_Negative turning points` | Jumlah titik lembah lokal di mana tren turun berbalik menjadi naik. | $84$ |
| 8 | `0_Positive turning points` | Jumlah titik puncak lokal di mana tren naik berbalik menjadi turun. | $85$ |
| 9 | `0_Neighborhood peaks` | Banyaknya puncak data lokal yang melampaui batas ambang tetangga terdekat. | $31$ |
| 10 | `0_Peak to peak distance` | Selisih rentang antara nilai maksimum absolut dan minimum absolut data. | $0,000089$ |
| 11 | `0_Slope` | Kemiringan garis regresi linier terhadap sumbu waktu (arah tren jangka panjang). | $-4,58 \times 10^{-8}$ |
| 12 | `0_Sum absolute differences` | Total akumulasi seluruh pergeseran dan fluktuasi nilai dari hari ke hari. | $0,002924$ |
| 13 | `0_Total energy` | Akumulasi integral diskrit energi sinyal pada rentang 366 hari. | $1,02 \times 10^{-6}$ |
| 14 | `0_Zero crossing rate` | Frekuensi perlintasan kurva terhadap nilai tengah (baseline) per satuan waktu. | $0,2650$ |
| 15 | `0_Entropy` | Ketidakteraturan atau kompleksitas dinamika fluktuasi sinyal. | $5,6214$ |
| 16 | `0_Max peaks` | Nilai magnitudo puncak tertinggi dalam observasi. | $0,000101$ |
| 17 | `0_Min peaks` | Nilai magnitudo lembah terendah dalam observasi. | $0,000012$ |
| 18 | `0_Number of crossing points` | Total kejadian saat sinyal memotong garis nilai rata-ratanya. | $97$ |

---

### C. Domain Spektral (Spectral Features)

Domain spektral diperoleh dengan mentransformasikan deret waktu ke domain frekuensi menggunakan transformasi Fourier (FFT), guna menemukan periodisitas mingguan, bulanan, maupun musiman dari emisi gas.

| No | Nama Fitur | Deskripsi Matematis & Fisis | Nilai Fitur |
| :---: | :--- | :--- | :--- |
| 1 | `0_FFT mean coefficient` | Rata-rata magnitudo spektral Fourier diskrit. | $0,000082$ |
| 2 | `0_Fundamental frequency` | Frekuensi dasar yang mendominasi komponen periodik deret waktu. | $0,00273$ |
| 3 | `0_Max power spectrum` | Nilai kerapatan spektral daya tertinggi (puncak energi frekuensi). | $4,85 \times 10^{-7}$ |
| 4 | `0_Maximum frequency` | Komponen batas frekuensi tertinggi yang memuat energi signifikan. | $0,50000$ |
| 5 | `0_Median frequency` | Frekuensi pembagi yang membagi dua luas total kerapatan spektrum. | $0,14208$ |
| 6 | `0_Spectral centroid` | Titik pusat massa kurva spektrum frekuensi Fourier. | $0,16541$ |
| 7 | `0_Spectral decrease` | Laju penurunan energi spektral seiring bertambahnya frekuensi. | $-0,000041$ |
| 8 | `0_Spectral distance` | Jarak deviasi bentuk spektrum terhadap spektrum referensi datar. | $0,78210$ |
| 9 | `0_Spectral energy` | Total energi kumulatif yang terkandung dalam spektrum daya FFT. | $2,18 \times 10^{-6}$ |
| 10 | `0_Spectral entropy` | Ukuran keacakan distribusi energi antarberbagai pita frekuensi. | $4,12890$ |
| 11 | `0_Spectral kurtosis` | Tingkat keruncingan distribusi magnitudo pada domain frekuensi. | $3,45120$ |
| 12 | `0_Spectral roll-off` | Frekuensi batas di mana $85\%$ dari total energi spektral berada di bawahnya. | $0,38798$ |
| 13 | `0_Spectral roll-on` | Frekuensi awal di mana energi spektral mulai mencapai ambang minimum $15\%$. | $0,02732$ |
| 14 | `0_Spectral skewness` | Derajat kemencengan distribusi kerapatan daya spektral. | $1,62400$ |
| 15 | `0_Spectral slope` | Gradien penurunan energi spektral pada skala logaritmik frekuensi. | $-0,00081$ |
| 16 | `0_Spectral spread` | Lebar dispersi (variansi) distribusi spektrum di sekitar spectral centroid. | $0,11940$ |
| 17 | `0_Spectral variation` | Variasi perubahan bentuk spektrum antarbin frekuensi berdekatan. | $0,34120$ |
| 18 | `0_Wavelet absolute mean` | Rata-rata absolut koefisien dekomposisi wavelet multi-resolusi. | $0,000031$ |
| 19 | `0_Wavelet energy` | Konsentrasi energi sinyal pada level aproksimasi wavelet. | $1,52 \times 10^{-7}$ |
| 20 | `0_Wavelet standard deviation` | Standar deviasi dari koefisien dekomposisi wavelet subband. | $0,000015$ |
| 21 | `0_Wavelet variance` | Variansi energi subband wavelet yang menangkap transien lokal. | $2,25 \times 10^{-10}$ |
| 22–35 | `0_Spectral band power (1–14)` | Pembagian daya spektral pada 14 sub-pita frekuensi harian hingga musiman. | Rentang $10^{-8}$ s.d. $10^{-10}$ |

---

## 4. Kesimpulan Ekstraksi

Kombinasi **68 fitur TSFEL** di atas menyederhanakan data deret waktu yang bervolume tinggi menjadi satu baris vektor fitur berdimensi 68. Vektor ini siap diintegrasikan ke dalam database cloud **PostgreSQL Aiven** dan diproses lebih lanjut menggunakan alur kerja visual **KNIME**.