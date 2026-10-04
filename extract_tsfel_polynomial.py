import pandas as pd
import numpy as np
import inspect
import tsfel.feature_extraction.features as tsfel_features


# ---------- 1. Muat file CSV semua polutan ----------
df = pd.read_csv(
    "Timeseries_CO_NO2_SO2_AsemRowo_Polynomial.csv"
)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

pollutants = ["NO2", "SO2", "CO"]
fs = 1


# ---------- 2. Daftar PERSIS 68 fitur yang diminta ----------
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


print(
    f"Jumlah fitur per polutan: "
    f"{len(FEATURE_LIST)}"
)

print(
    f"Total target fitur keseluruhan: "
    f"{len(FEATURE_LIST) * len(pollutants)}"
)


def to_scalar(result):
    if (
        isinstance(result, dict)
        and "values" in result
    ):
        result = result["values"]

    if isinstance(
        result,
        (list, tuple, np.ndarray),
    ):
        arr = np.asarray(
            result,
            dtype=float,
        )

        return float(
            np.nanmean(arr)
        )

    return float(result)


def extract_one(
    fn_name,
    signal,
    fs,
):
    fn = getattr(
        tsfel_features,
        fn_name,
    )

    params = inspect.signature(
        fn
    ).parameters

    if "fs" in params:
        result = fn(
            signal,
            fs,
        )
    else:
        result = fn(signal)

    return to_scalar(result)


# Dictionary untuk menampung seluruh hasil ekstraksi
combined_row = {}


# ---------- 3. Ekstraksi setiap polutan ----------
for pollutant in pollutants:
    print(
        f"\n--- Memproses polutan: "
        f"{pollutant} ---"
    )

    # Membuat salinan dataframe
    df_poly = df[
        ["date", pollutant]
    ].copy()

    # Memastikan nilai berupa numerik
    df_poly[pollutant] = pd.to_numeric(
        df_poly[pollutant],
        errors="coerce",
    )

    n_missing_before = (
        df_poly[pollutant]
        .isna()
        .sum()
    )

    print(
        f"Jumlah NaN/non-numerik pada "
        f"{pollutant}: {n_missing_before}"
    )

    # Handling outlier menggunakan IQR
    Q1 = df_poly[pollutant].quantile(
        0.25
    )

    Q3 = df_poly[pollutant].quantile(
        0.75
    )

    IQR = Q3 - Q1

    lower_bound = (
        Q1 - 1.5 * IQR
    )

    upper_bound = (
        Q3 + 1.5 * IQR
    )

    kondisi_outlier = (
        (df_poly[pollutant] < lower_bound)
        | (df_poly[pollutant] > upper_bound)
    )

    df_poly.loc[
        kondisi_outlier,
        pollutant,
    ] = np.nan

    # Interpolasi waktu dan cleaning
    df_clean = (
        df_poly
        .set_index("date")
        .interpolate(method="time")
        .ffill()
        .bfill()
    )

    signal_1d = (
        df_clean[pollutant]
        .astype(float)
        .values
    )

    # Ekstraksi fitur dan pemberian prefix polutan
    for fn_name in FEATURE_LIST:
        feature_key = (
            f"{pollutant}_{fn_name}"
        )

        combined_row[feature_key] = (
            extract_one(
                fn_name,
                signal_1d,
                fs,
            )
        )


# ---------- 4. Simpan hasil 1 baris dan 204 kolom ----------
extracted_features_final = (
    pd.DataFrame([combined_row])
)


print(
    "\nBerhasil! Total kolom akhir "
    "yang dihasilkan: "
    f"{extracted_features_final.shape[1]}"
)


# Pemeriksaan hasil akhir
jumlah_missing = (
    extracted_features_final
    .isna()
    .sum()
    .sum()
)

jumlah_infinity = np.isinf(
    extracted_features_final
    .to_numpy(dtype=float)
).sum()


print(
    "Ukuran hasil:",
    extracted_features_final.shape,
)

print(
    "Missing value:",
    jumlah_missing,
)

print(
    "Infinity:",
    jumlah_infinity,
)


output_filename = (
    "All-Pollutants-AsemRowo-TSFEL-Polynomial.csv"
)

extracted_features_final.to_csv(
    output_filename,
    index=False,
)


print(
    "File berhasil disimpan sebagai:",
    output_filename,
)