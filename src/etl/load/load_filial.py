import pandas as pd
import logging
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Gold_Filial")

def load_filial():
    logger.info("Iniciando a carga da Dimensão Filial a partir da camada Silver...")
    
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query_silver = """
            SELECT 
                codigo_filial AS id_filial, 
                codigo_regiao AS id_regiao 
            FROM silver.filial_clean
        """
        cursor.execute(query_silver)
        
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            logger.warning("A camada Silver de filiais está vazia. Abortando processo de carga na Gold.")
            return

        logger.info(f"{len(df)} registros de filiais recuperados da Silver. Iniciando inserção...")

        insert_sql = """
            INSERT INTO gold.filial (id_filial, nome_filial, id_regiao)
            VALUES (%s, %s, %s)
            ON CONFLICT (id_filial) DO NOTHING;
        """

        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                int(row["id_filial"]),
                "Filial " + str(row["id_filial"]),
                int(row["id_regiao"])
            ))

        conn.commit()
        logger.info(f"Carga finalizada com sucesso! Filiais inseridas/verificadas na Gold.")

    except Exception as e:
        logger.error(f"Erro crítico durante a carga da dimensão filial: {e}", exc_info=True)
        if conn: 
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Conexão com o banco encerrada para esta tarefa.")

if __name__ == "__main__":
    load_filial()