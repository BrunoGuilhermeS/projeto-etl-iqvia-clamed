from src.etl.convert_csv.converter_csv import convert_filial_brick
import psycopg2 as pg
import pandas as pd

print('ok')


convert_filial_brick("./data/xlsx_raw/MS_12_2022_sample.xlsx")


def load_regiao():
    ...


def load_produto():
    ...
