import pandas as pd
import numpy as np
import logging
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Silver_MarketSales")

def silver_market_sales_transform():
    conn = None
    cur = None
    
    try:
        logger.info("Iniciando a transformação da camada Silver (Market Sales).")
        
        conn = get_connection()
        cur = conn.cursor()

        logger.info("Lendo dados da tabela bronze.market_sales_raw...")
        cur.execute("SELECT * FROM bronze.market_sales_raw")
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=columns)

        if df.empty:
            logger.warning("A tabela bronze.market_sales_raw está vazia. Processo interrompido.")
            return

        logger.info(f"{len(df)} registros encontrados. Iniciando transformações...")

        df["nome_produto"] = None 
        df["cod_regiao"] = df["brick"].astype(str).str.split(" - ").str[0].str.strip()
        
        df = df.rename(columns={
            "ean": "cod_ean",
            "si_conc_un": "si_conc_un",
            "so_conc_un": "so_conc_un",
            "pp_un": "pp_un"
        })

        cols_numeric = ["si_conc_un", "so_conc_un", "pp_un"]
        df[cols_numeric] = df[cols_numeric].fillna(0)

        logger.info("Limpando tabela silver.market_sales_clean (TRUNCATE)...")
        cur.execute("TRUNCATE TABLE silver.market_sales_clean")

        insert_query = """
            INSERT INTO silver.market_sales_clean (
                cod_regiao, cod_ean, cod_prod_catarinense, 
                si_conc_un, so_conc_un, pp_un, nome_produto, periodo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        logger.info("Inserindo dados transformados...")
        for _, row in df.iterrows():
            cur.execute(insert_query, (
                row["cod_regiao"],
                row["cod_ean"],
                row["cod_prod_catarinense"],
                row["si_conc_un"],
                row["so_conc_un"],
                row["pp_un"],
                row["nome_produto"],
                row["periodo"]
            ))

        conn.commit()
        logger.info(f"Sucesso! {len(df)} registros processados e inseridos na silver.market_sales_clean com período.")

    except Exception as e:
        logger.error(f"Erro crítico na carga Silver (Market Sales): {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()