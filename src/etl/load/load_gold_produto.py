import psycopg2 as pg
import pandas as pd
from src.etl.db.connection import get_connection
import os

def load_gold_produtos():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT cod_ean, nome_produto, cod_prod_catarinense FROM silver.market_sales_clean")
    produtos = cur.fetchall()

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
        cur.execute(sql_insert, (
            prod[0],
            prod[0],
            prod[2],
            prod[1] if prod[1] else "PRODUTO SEM NOME"
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    print("Tabela Gold de Produtos populada com sucesso!")

if __name__ == "__main__":
    load_gold_produtos()