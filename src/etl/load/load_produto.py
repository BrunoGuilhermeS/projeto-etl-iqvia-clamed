import os
import pandas as pd
from src.db.connection import get_connection


def load_produtos():

    df = pd.read_csv("../data/clean_datasets/filial_clean.csv")

    df_produtos = df[["cod_cean", "cod_prod",
                      "nome_produto"]].drop_duplicates()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO produtos (cod_cean, cod_prod, nome_produto)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
        """

        for _, row in df_produtos.iterrows():
            cursor.execute(insert_sql,
                           (str(row['cod_cean']), str(row['cod_prod']) if not pd.isna(row["cod_prod"]) else None, row['nome_produto']
                            )
                           )

        conn.commit()
        print("Produtos carregados com sucesso!")

    except Exception as e:
        print("Erro ao carregar produtos!", e)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_produtos()
