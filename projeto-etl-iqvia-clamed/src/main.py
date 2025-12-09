import psycopg2 as pg
import pandas as pd

print('ok')

from src.convert_csv.converter_csv import convert_filial_brick

convert_filial_brick("./data/xlsx_raw/MS_12_2022_sample.xlsx")

