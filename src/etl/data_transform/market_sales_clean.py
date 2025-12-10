import pandas as pd
import numpy as np

df = pd.read_csv("data/csv_raw/MS_12_2022_sample.csv")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# Corrigindo nome das colunas
df = df.rename(columns={
    "BRICK": "cod_regiao",
    "EAN": "cod_ean",
    "Cod Prod Catarinense": "cod_prod_catarinense",
    "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "SI_CONC_UN",
    "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "SO_CONC_UN",
    "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "PP_UN"
})

# Gerando a coluna com os futuros nomes desses produtos

df["nome_produto"] = np.nan

# Corrigindo coluna cod_regiao, para ficar somento com o codigo

df["cod_regiao"] = df["cod_regiao"].astype(
    str).str.split(" - ").str[0].str.replace(" ", "")

# Preenchendo NaN com 0

df["SI_CONC_UN"] = df["SI_CONC_UN"].fillna(0)
df["SO_CONC_UN"] = df["SO_CONC_UN"].fillna(0)
df["PP_UN"] = df["PP_UN"].fillna(0)

df.to_csv("data/clean_datasets/market_sales_12_2022.csv")

print(df.head())
