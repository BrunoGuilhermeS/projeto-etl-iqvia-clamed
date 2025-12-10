from src.etl.convert_csv.converter_csv import convert_filial_brick
from src.etl.load.load_regiao import load_regiao
from src.etl.load.load_produto import load_produtos
import psycopg2 as pg
import pandas as pd

print('ok')

convert_filial_brick("./data/xlsx_raw/MS_12_2022_sample.xlsx")

load_regiao()
load_produtos()
