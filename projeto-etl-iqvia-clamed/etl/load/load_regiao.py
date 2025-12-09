import psycopg2 as pg
import pandas as pd
import sys
import os
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(ROOT_PATH)
from src.db.connection import get_connection


def load_regiao():

    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    csv_path = os.path.join(ROOT, "data", "clean_datasets", "filial_clean.csv")

    df = pd.read_csv(csv_path)

    #print(df.head())

    df_regiao = df[["codigo_regiao", "regiao"]].drop_duplicates()

    try:
        conn = get_connection()
        cur = conn.cursor()

        insert_sql = """INSERT INTO regiao(id_regiao, nome_regiao)
                    VALUES (%s, %s)
                    ON CONFLICT (id_regiao) DO NOTHING;
        """
        for _, row in df_regiao.iterrows():
            cur.execute(insert_sql,(int(row["codigo_regiao"]), row["regiao"]))

            conn.commit()
            print("Regiões carregadas com sucesso!")

    except Exception as e:
        print("Erro ao inserir regiões:", e)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_regiao()