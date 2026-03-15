import pandas as pd
from src.etl.db.connection import get_connection


def load_filial_raw(input_path):

    conn = get_connection()

    df = pd.read_csv(input_path)

    df = df.rename(columns={
        "brick": "brick",
        "Cód. Filial": "cod_filial"
    })

    df.to_sql(
        "filial_raw",
        con=conn,
        schema="bronze",
        if_exists="append",
        index=False
    )

    conn.close()

    print("Filial carregada na camada Bronze")


def load_market_sales_raw(input_path):

    conn = get_connection()

    df = pd.read_csv(input_path)

    df = df.rename(columns={
        "BRICK": "brick",
        "EAN": "ean",
        "Cod Prod Catarinense": "cod_prod_catarinense",
        "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "si_conc_un",
        "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "so_conc_un",
        "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "pp_un"
    })

    df.to_sql(
        "market_sales_raw",
        con=conn,
        schema="bronze",
        if_exists="append",
        index=False
    )

    conn.close()

    print("Market sales carregado na camada Bronze")