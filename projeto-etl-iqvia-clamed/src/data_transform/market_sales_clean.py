import pandas as pd

df = pd.read_csv("../../data/csv_raw/MS_12_2022_sample.csv")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

#Corrigindo nome das colunas
df= df.rename(columns={
    "BRICK": "cod_regiao",
    "EAN": "codigo_ean",
    "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "(SI) Bandeira Indenpendente Concorrente (Un)",
    "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "(SO) Bandeira Organizada Concorrente (Un)",
    "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "(PP) Bandeira Preco Popular (Un)"
})

#Corrigindo coluna cod_regiao, para ficar somento com o codigo

df["cod_regiao"] = df["cod_regiao"].astype(str).str.split(" - ").str[0].str.replace(" ","")

#Preenchendo NaN com 0

df["(SI) Bandeira Indenpendente Concorrente (Un)"] = (
    df["(SI) Bandeira Indenpendente Concorrente (Un)"].fillna(0)
)

df["(SO) Bandeira Organizada Concorrente (Un)"] = (
    df["(SO) Bandeira Organizada Concorrente (Un)"].fillna(0)
)

df["(PP) Bandeira Preco Popular (Un)"] = (
    df["(PP) Bandeira Preco Popular (Un)"].fillna(0)
)

df.to_csv("../../data/clean_datasets/market_sales_12_2022.csv")

print(df.head())

