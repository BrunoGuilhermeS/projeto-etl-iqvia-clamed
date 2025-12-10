from src.etl.convert_csv.converter_csv import convert_filial_brick
from src.etl.load.load_regiao import load_regiao
from src.etl.load.load_produto import load_produto
from src.etl.load.load_filial import load_filial
import psycopg2 as pg
import pandas as pd

print('ok')

convert_filial_brick("./data/xlsx_raw/MS_12_2022_sample.xlsx")

#load_regiao()
#load_produto()
load_filial()
