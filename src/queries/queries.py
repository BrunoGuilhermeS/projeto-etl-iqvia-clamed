import pandas as pd
from src.etl.db.connection import get_connection

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
            v.periodo,
            r.nome_regiao as regiao,
            b.nome_bandeira as bandeira,
            b.tipo_bandeira,
            v.volume_venda,
            p.valor_produto,
            p.nome_produto,
            -- Aqui pegamos o código que você mostrou nos dados (ex: '734398')
            p.sk_produto as ean_produto 
        FROM gold.volume_vendas v
            JOIN gold.produtos p ON v.sk_produto = p.sk_produto
            JOIN gold.bandeira b ON v.id_bandeira = b.id_bandeira
            JOIN gold.regiao r ON v.id_regiao = r.id_regiao
    """

    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()
