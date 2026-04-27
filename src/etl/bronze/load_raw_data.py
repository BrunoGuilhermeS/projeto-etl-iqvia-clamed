import pandas as pd
import os
import re
import logging
from src.etl.db.connection import get_connection

# Inicializa o logger para a camada Bronze
logger = logging.getLogger("ETL_Bronze")

def load_filial_raw(input_path):
    conn = None
    cur = None
    
    try:
        logger.info(f"Iniciando carga de filiais (Bronze). Arquivo: {input_path}")
        df = pd.read_csv(str(input_path))
        logger.info(f"{len(df)} registros lidos do CSV.")

        df = df.rename(columns={
            "Cód. Filial": "cod_filial",
        })

        conn = get_connection()
        cur = conn.cursor()

        logger.info("Inserindo dados de filiais...")
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
        logger.info("Sucesso! Filiais carregadas na camada Bronze.")

    except Exception as e:
        logger.error(f"Erro crítico ao carregar filial na camada Bronze: {e}", exc_info=True)
        if conn: 
            conn.rollback()
    finally:
        if cur: 
            cur.close()
        if conn: 
            conn.close()


def load_market_sales_raw(input_path):
    file_name = os.path.basename(input_path)
    logger.info(f"Processando arquivo Market Sales (Bronze): {file_name}")
    
    # Capturar mês e ano
    match = re.search(r"(\d{2})_(\d{4})", file_name)

    if match:
        mes = match.group(1)
        ano = match.group(2)
        periodo_extraido = f"{ano}-{mes}-01" 
        logger.info(f"Período extraído do nome do arquivo: {periodo_extraido}")
    else:
        periodo_extraido = None 
        logger.warning(f"Aviso: Período não encontrado no nome do arquivo {file_name}.")

    conn = None
    cur = None

    try:
        df = pd.read_csv(input_path)
        logger.info(f"{len(df)} registros lidos do CSV.")
        
        df = df.rename(columns={
            "BRICK": "brick",
            "EAN": "ean",
            "Cod Prod Catarinense": "cod_prod_catarinense",
            "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "si_conc_un",
            "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "so_conc_un",
            "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "pp_un"
        })

        conn = get_connection()
        cur = conn.cursor()
        
        logger.info("Limpando tabela bronze.market_sales_raw (TRUNCATE)...")
        cur.execute("TRUNCATE TABLE bronze.market_sales_raw")

        insert_sql = """
            INSERT INTO bronze.market_sales_raw (
                brick, ean, cod_prod_catarinense, 
                si_conc_un, so_conc_un, pp_un, periodo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        logger.info("Inserindo dados de Market Sales...")
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
        logger.info(f"Sucesso! Market sales ({periodo_extraido}) carregado na camada Bronze.")

    except Exception as e:
        logger.error(f"Erro ao carregar Market Sales na Bronze: {e}", exc_info=True)
        if conn: 
            conn.rollback()
    finally:
        if cur: 
            cur.close()
        if conn: 
            conn.close()