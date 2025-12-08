import os
import pandas as pd

def convert_filial_brick(file):
    filename = os.path.splitext(os.path.basename(file))[0]
    csv_path = f"./data/csv_raw/{filename}.csv"

    df = pd.read_excel(file)
    df.to_csv(csv_path, index=False)