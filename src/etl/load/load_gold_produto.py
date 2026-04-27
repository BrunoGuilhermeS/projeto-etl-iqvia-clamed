import logging
import pandas as pd
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Gold_Produtos")

def load_gold_produtos():
    logger.info("Iniciando o carregamento da Dimensão Produtos (Gold)...")
    
    conn = None
    cur = None
    
    try:
        conn = get_connection()
        cur = conn.cursor()

        logger.info("Recuperando produtos distintos da camada Silver...")
        query_silver = """
            SELECT DISTINCT cod_ean, nome_produto, cod_prod_catarinense 
            FROM silver.market_sales_clean
        """
        cur.execute(query_silver)
        produtos = cur.fetchall()

        if not produtos:
            logger.warning("Nenhum produto encontrado na camada Silver. Abortando carga.")
            return

        logger.info(f"{len(produtos)} produtos identificados para processamento.")

        sql_insert = """
            INSERT INTO gold.produtos (
                id_produto_original, 
                cod_ean, 
                cod_prod_catarinense, 
                nome_produto, 
                data_inicio_validade, 
                flag_ativo
            )
            VALUES (%s, %s, %s, %s, CURRENT_DATE, TRUE)
            ON CONFLICT (id_produto_original) WHERE flag_ativo = TRUE DO NOTHING;
        """
        
        for prod in produtos:
            # prod[0] = cod_ean, prod[1] = nome_produto, prod[2] = cod_prod_catarinense
            cur.execute(sql_insert, (
                prod[0],
                prod[0],
                prod[2],
                prod[1] if prod[1] else "PRODUTO SEM NOME"
            ))
        
        conn.commit()
        logger.info("Tabela Gold de Produtos populada/atualizada com sucesso!")

    except Exception as e:
        logger.error(f"Erro crítico ao carregar produtos na Gold: {e}", exc_info=True)
        if conn:
            conn.rollback()
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        logger.info("Conexão com o banco encerrada.")

if __name__ == "__main__":
    load_gold_produtos()