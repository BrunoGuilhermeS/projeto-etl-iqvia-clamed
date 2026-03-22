import pandas as pd
from src.etl.db.connection import get_connection

def load_filial():
    print("Carregando Dimensão Filial a partir da Silver...")
    
    conn = None
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
            print("⚠️ Camada Silver de filiais está vazia. Abortando carga.")
            return

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
        print("Filiais carregadas com sucesso na Gold!")

    except Exception as e:
        print(f"Erro ao inserir filiais: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    load_filial()