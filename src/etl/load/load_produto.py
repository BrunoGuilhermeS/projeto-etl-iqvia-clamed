import psycopg2 as pg
import pandas as pd
from src.etl.db.connection import get_connection
import os


def load_produto():

    ROOT = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../../../"))
    csv_path = os.path.join(
        ROOT, "data", "clean_datasets", "market_sales_12_2022.csv")

    df = pd.read_csv(csv_path)

    df_produtos = df[["cod_ean", "cod_prod_catarinense",
                      "nome_produto"]].drop_duplicates().copy()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_sql = """
            INSERT INTO gold.produtos (
                id_produto_original,
                cod_ean,
                cod_prod_catarinense,
                nome_produto,
                data_inicio_validade,
                flag_ativo
            )
            -- Note que agora temos 4 placeholders e 2 valores fixos, totalizando 6
            VALUES (%s, %s, %s, %s, CURRENT_DATE, TRUE) 
            ON CONFLICT DO NOTHING;
        """

        for _, row in df_produtos.iterrows():
            id_original = int(row['cod_ean']) 
            
            # A tupla abaixo tem exatamente 4 itens, batendo com os 4 %s acima
            cursor.execute(insert_sql, (
                id_original,
                int(row['cod_ean']),
                str(int(row['cod_prod_catarinense'])) if not pd.isna(row["cod_prod_catarinense"]) else None,
                row['nome_produto']
            ))

        conn.commit()
        print("Produtos carregados com sucesso!")

    except Exception as e:
        print("Erro ao carregar produtos!", e)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_produto()
