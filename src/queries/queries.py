import pandas as pd
from src.etl.db.connection import get_connection

# src/analysis/queries.py

# Abrir conexão
def select_df(sql: str, params=None):
    conn = get_connection()
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df


def get_regiao():
    return select_df("SELECT * FROM gold.regiao")


def get_bandeira():
    return select_df("SELECT * FROM gold.bandeira")


def get_produtos():
    return select_df("SELECT * FROM gold.produtos")


def get_volume_vendas():
    return select_df("SELECT * FROM gold.volume_vendas")


def get_volume_com_dimensoes():
    sql = """
        SELECT
            r.nome_regiao,
            b.nome_bandeira,
            p.cod_ean,
            v.volume_venda,
            v.periodo
        FROM gold.volume_vendas v
        JOIN regiao r    ON r.id_regiao = v.id_regiao
        JOIN bandeira b  ON b.id_bandeira = v.id_bandeira
        JOIN produtos p  ON p.id_produto = v.id_produto;
        """
    return select_df(sql)
