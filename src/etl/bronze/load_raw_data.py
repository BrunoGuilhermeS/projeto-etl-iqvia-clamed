import pandas as pd
import os
import re
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
    # Extrair o nome do arquivo
    file_name = os.path.basename(input_path)
    
    # Capturar mês e ano
    match = re.search(r"(\d{2})_(\d{4})", file_name)

    if match:
        mes = match.group(1)
        ano = match.group(2)
        # Formata para o padrão ISO: YYYY-MM-DD (Sempre dia 01)
        periodo_extraido = f"{ano}-{mes}-01" 
    else:
        # Se não encontrar a data, você pode definir um valor padrão ou interromper
        periodo_extraido = None 
        print("Aviso: Período não encontrado no nome do arquivo.")

    print(f"Extraindo dados para o período formatado: {periodo_extraido}")

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Carregar o CSV
        df = pd.read_csv(input_path)
        
        # Renomear as colunas
        df = df.rename(columns={
            "BRICK": "brick",
            "EAN": "ean",
            "Cod Prod Catarinense": "cod_prod_catarinense",
            "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "si_conc_un",
            "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "so_conc_un",
            "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "pp_un"
        })

        # Inserir os dados
        cur.execute("TRUNCATE TABLE bronze.market_sales_raw")

        insert_sql = """
            INSERT INTO bronze.market_sales_raw (
                brick, ean, cod_prod_catarinense, 
                si_conc_un, so_conc_un, pp_un, periodo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            cur.execute(insert_sql, (
                row["brick"],
                row["ean"],
                row["cod_prod_catarinense"],
                row["si_conc_un"],
                row["so_conc_un"],
                row["pp_un"],
                periodo_extraido
            ))

        conn.commit()
        print(f"Market sales ({periodo_extraido}) carregado na camada Bronze")

    except Exception as e:
        if conn: conn.rollback()
        print(f"Erro ao carregar Bronze: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()

    print("Market sales carregado na camada Bronze")