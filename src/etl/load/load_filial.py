from src.etl.db.connection import get_connection
import pandas as pd
import os

def load_filial():
    csv_path = os.path.join("data", "clean_datasets", "filial_clean.csv")
    df = pd.read_csv(csv_path) 
    df_filial = df[["codigo_filial", "codigo_regiao"]].copy()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO filial (id_filial, nome_filial, id_regiao)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        """

        for _, row in df_filial.iterrows():
            cursor.execute(insert_sql, (
                int(row["codigo_filial"]),
                "Desconhecido",
                int(row["codigo_regiao"])
                )
                )

        conn.commit()  # commit depois de inserir tudo
        print("Filiais carregadas com sucesso")

    except Exception as e:
        print("Erro ao inserir filiais:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_filial()
