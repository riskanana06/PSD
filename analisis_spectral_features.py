from pathlib import Path

import pandas as pd
from tsfel.feature_extraction.features import (
    spectral_decrease,
    spectral_distance,
)

folder = Path(__file__).parent
fs = 1  # Satu sampel setiap hari

data_polutan = {
    "CO": "CO_AsemRowo_Timeseries_Clean.csv",
    "NO2": "NO2_AsemRowo_Timeseries_Clean.csv",
    "SO2": "SO2_AsemRowo_Timeseries_Clean.csv",
}

hasil = []

for polutan, nama_file in data_polutan.items():
    df = pd.read_csv(folder / nama_file)
    sinyal = df[polutan].astype(float).to_numpy()

    hasil.append(
        {
            "polutan": polutan,
            "spectral_decrease": spectral_decrease(sinyal, fs),
            "spectral_distance": spectral_distance(sinyal, fs),
        }
    )

df_hasil = pd.DataFrame(hasil)

print("\nHasil Ekstraksi Fitur Spectral:")
print(df_hasil.to_string(index=False))

output = folder / "Hasil_Spectral_Decrease_Distance.csv"
df_hasil.to_csv(output, index=False)

print("\nFile berhasil disimpan:")
print(output)