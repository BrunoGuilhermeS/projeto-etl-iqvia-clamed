import pandas as pd
import logging
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Gold_Regiao")

def load_regiao():
    logger.info("Iniciando a carga da Dimensão Região a partir da camada Silver...")
    
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT 
                codigo_regiao AS id_regiao, 
                regiao AS nome_regiao 
            FROM silver.filial_clean
            WHERE codigo_regiao IS NOT NULL
        """
        
        logger.info("Buscando regiões distintas na tabela silver.filial_clean...")
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            logger.warning("A tabela Silver de filiais está vazia. Nenhuma região para carregar.")
            return

        logger.info(f"{len(df)} regiões encontradas. Preparando banco de dados...")

        # Limpeza da tabela Gold (CASCADE garante que as chaves estrangeiras não travem o processo)
        logger.info("Executando TRUNCATE na tabela gold.regiao (CASCADE)...")
        cursor.execute("TRUNCATE TABLE gold.regiao CASCADE;")

        sql_insert = """
            INSERT INTO gold.regiao (id_regiao, nome_regiao)
            VALUES (%s, %s)
            ON CONFLICT (id_regiao) DO NOTHING;
        """

        logger.info("Inserindo regiões na camada Gold...")
        for _, row in df.iterrows():
            cursor.execute(sql_insert, (
                row["id_regiao"],
                row["nome_regiao"]
            ))

        conn.commit()
        logger.info("Sucesso! Dimensão Região carregada e atualizada na Gold.")

    except Exception as e:
        logger.error(f"Erro crítico ao carregar região na Gold: {e}", exc_info=True)
        if conn: 
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Conexão com o banco encerrada.")

if __name__ == "__main__":
    load_regiao()