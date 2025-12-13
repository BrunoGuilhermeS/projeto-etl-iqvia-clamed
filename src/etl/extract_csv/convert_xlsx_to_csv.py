import os
import pandas as pd


def convert_all_xlsx_in_folder(
    input_dir: str = "data/xlsx_raw",
    output_dir: str = "data/csv_raw"
):
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".xlsx"):
            input_path = os.path.join(input_dir, file)

            filename = os.path.splitext(file)[0]
            output_path = os.path.join(output_dir, f"{filename}.csv")

            df = pd.read_excel(input_path)
            df.to_csv(output_path, index=False)

            print(f"Convertido: {file}")
