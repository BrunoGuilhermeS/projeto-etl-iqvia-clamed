import pandas as pd
from src.etl.db.connection import get_connection

def load_filial_raw(input_path):

    df = pd.read_csv(str(input_path))

    df = df.rename(columns={
        "Cód. Filial": "cod_filial",
    })

    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO bronze.filial_raw (
                cod_filial,
                brick
            )
            VALUES (%s,%s)
        """, (
            row["cod_filial"],
            row["brick"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    print("Filial carregada na camada Bronze")


def load_market_sales_raw(input_path):

    conn = get_connection()
    cur = conn.cursor()

    df = pd.read_csv(input_path)
    df = df.rename(columns={
        "BRICK": "brick",
        "EAN": "ean",
        "Cod Prod Catarinense": "cod_prod_catarinense",
        "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "si_conc_un",
        "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "so_conc_un",
        "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "pp_un"
    })

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO bronze.market_sales_raw (
                brick,
                ean,
                cod_prod_catarinense,
                si_conc_un,
                so_conc_un,
                pp_un
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["brick"],
            row["ean"],
            row["cod_prod_catarinense"],
            row["si_conc_un"],
            row["so_conc_un"],
            row["pp_un"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    print("Market sales carregado na camada Bronze")