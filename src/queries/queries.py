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
            r.nome_regiao,
            b.nome_bandeira,
            p.cod_ean,
            v.volume_venda,
            v.periodo
        FROM gold.volume_vendas v
        JOIN gold.regiao r    ON r.id_regiao = v.id_regiao
        JOIN gold.bandeira b  ON b.id_bandeira = v.id_bandeira
        JOIN gold.produtos p  ON p.sk_produto = v.sk_produto;
    """
    
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn)
        return df
    except Exception as e:
        # ISSO VAI MOSTRAR O ERRO REAL NO TERMINAL
        print(f"\n--- ERRO DO BANCO DE DADOS ---")
        print(e)
        print(f"------------------------------\n")
        raise e # Relança o erro para sabermos que falhou
    finally:
        conn.close()
