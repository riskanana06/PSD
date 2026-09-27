import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import tsfel.feature_extraction.features as tsfel_features


folder_materi = Path(__file__).parent
fs = 1  # Satu sampel per hari


FEATURE_LIST = """
abs_energy
auc
autocorr
average_power
calc_centroid
calc_max
calc_mean
calc_median
calc_min
calc_std
calc_var
dfa
distance
ecdf
ecdf_percentile
ecdf_percentile_count
ecdf_slope
entropy
fundamental_frequency
higuchi_fractal_dimension
hist_mode
human_range_energy
hurst_exponent
interq_range
kurtosis
lempel_ziv
lpcc
max_frequency
max_power_spectrum
maximum_fractal_length
mean_abs_deviation
mean_abs_diff
mean_diff
median_abs_deviation
median_abs_diff
median_diff
median_frequency
mfcc
mse
negative_turning
neighbourhood_peaks
petrosian_fractal_dimension
pk_pk_distance
positive_turning
power_bandwidth
rms
skewness
slope
spectral_centroid
spectral_decrease
spectral_distance
spectral_entropy
spectral_kurtosis
spectral_positive_turning
spectral_roll_off
spectral_roll_on
spectral_skewness
spectral_slope
spectral_spread
spectral_variation
spectrogram_mean_coeff
sum_abs_diff
wavelet_abs_mean
wavelet_energy
wavelet_entropy
wavelet_std
wavelet_var
zero_cross
""".split()


if len(FEATURE_LIST) != 68:
    raise ValueError(
        f"Jumlah fitur bukan 68: {len(FEATURE_LIST)}"
    )


def ubah_ke_skalar(hasil):
    if isinstance(hasil, dict) and "values" in hasil:
        hasil = hasil["values"]

    if isinstance(
        hasil,
        (list, tuple, np.ndarray),
    ):
        array = np.asarray(
            hasil,
            dtype=float,
        )

        return float(
            np.nanmean(array)
        )

    return float(hasil)


def ekstrak_satu_fitur(
    nama_fitur,
    sinyal,
    sampling_frequency,
):
    fungsi = getattr(
        tsfel_features,
        nama_fitur,
    )

    parameter = inspect.signature(
        fungsi
    ).parameters

    if "fs" in parameter:
        hasil = fungsi(
            sinyal,
            sampling_frequency,
        )
    else:
        hasil = fungsi(sinyal)

    return ubah_ke_skalar(hasil)


def ekstrak_polutan(nama_polutan):
    input_file = (
        folder_materi
        / f"{nama_polutan}_AsemRowo_Timeseries_Clean.csv"
    )

    df = pd.read_csv(input_file)

    sinyal = (
        df[nama_polutan]
        .astype(float)
        .to_numpy()
    )

    if np.isnan(sinyal).any():
        raise ValueError(
            f"{nama_polutan} masih memiliki missing value."
        )

    if (sinyal < 0).any():
        raise ValueError(
            f"{nama_polutan} masih memiliki nilai negatif."
        )

    hasil_fitur = {}
    fitur_gagal = []

    for nama_fitur in FEATURE_LIST:
        try:
            hasil_fitur[nama_fitur] = (
                ekstrak_satu_fitur(
                    nama_fitur,
                    sinyal,
                    fs,
                )
            )

            print(
                f"{nama_polutan}: "
                f"{nama_fitur} berhasil"
            )

        except Exception as error:
            fitur_gagal.append(
                f"{nama_fitur}: {error}"
            )

    if fitur_gagal:
        print(
            f"\nFitur gagal pada {nama_polutan}:"
        )

        for pesan in fitur_gagal:
            print(pesan)

        raise RuntimeError(
            f"Ekstraksi {nama_polutan} belum lengkap."
        )

    df_fitur = pd.DataFrame(
        [hasil_fitur]
    )

    output_file = (
        folder_materi
        / f"{nama_polutan}_AsemRowo_TSFEL_68_Clean.csv"
    )

    df_fitur.to_csv(
        output_file,
        index=False,
    )

    print(
        f"\n{nama_polutan} selesai: "
        f"{df_fitur.shape}"
    )

    return df_fitur


semua_fitur = {}


for polutan in ["CO", "NO2", "SO2"]:
    semua_fitur[polutan] = (
        ekstrak_polutan(polutan)
    )


# Gabungkan menjadi 204 kolom
fitur_gabungan = pd.concat(
    [
        semua_fitur["CO"].add_prefix("CO_"),
        semua_fitur["NO2"].add_prefix("NO2_"),
        semua_fitur["SO2"].add_prefix("SO2_"),
    ],
    axis=1,
)


if fitur_gabungan.shape != (1, 204):
    raise ValueError(
        "Ukuran fitur gabungan tidak sesuai: "
        f"{fitur_gabungan.shape}"
    )


output_gabungan = (
    folder_materi
    / "AsemRowo_TSFEL_204_Clean.csv"
)

fitur_gabungan.to_csv(
    output_gabungan,
    index=False,
)


print("\nEkstraksi seluruh polutan berhasil.")
print("Ukuran fitur gabungan:", fitur_gabungan.shape)
print("Missing value:", fitur_gabungan.isna().sum().sum())
print("File:", output_gabungan)