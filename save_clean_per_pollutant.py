from pathlib import Path

import pandas as pd


folder_materi = Path(__file__).parent

input_file = (
    folder_materi
    / "Timeseries_CO_NO2_SO2_AsemRowo_Clean.csv"
)

df = pd.read_csv(input_file)
df["date"] = pd.to_datetime(df["date"])


file_output = {
    "CO": "CO_AsemRowo_Timeseries_Clean.csv",
    "NO2": "NO2_AsemRowo_Timeseries_Clean.csv",
    "SO2": "SO2_AsemRowo_Timeseries_Clean.csv",
}


for polutan, nama_file in file_output.items():
    data_polutan = df[["date", polutan]].copy()

    output_path = folder_materi / nama_file

    data_polutan.to_csv(
        output_path,
        index=False,
    )

    print(
        f"{nama_file}: "
        f"{data_polutan.shape[0]} baris, "
        f"{data_polutan[polutan].isna().sum()} missing"
    )