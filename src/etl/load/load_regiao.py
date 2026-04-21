import pandas as pd
from src.etl.db.connection import get_connection

def load_regiao():
    print("Carregando Dimensão Região a partir da Silver...")
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # --- A CULPADA ESTAVA AQUI ---
        # Trocamos a concatenação boba pelo nome real da coluna: "regiao"
        query = """
            SELECT DISTINCT 
                codigo_regiao AS id_regiao, 
                regiao AS nome_regiao 
            FROM silver.filial_clean
            WHERE codigo_regiao IS NOT NULL
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            print("Tabela Silver de filiais está vazia.")
            return

        # Dica: É bom limpar a tabela antes de carregar a dimensão novamente
        # caso você esteja testando várias vezes
        cursor.execute("TRUNCATE TABLE gold.regiao CASCADE;")

        sql_insert = """
            INSERT INTO gold.regiao (id_regiao, nome_regiao)
            VALUES (%s, %s)
            ON CONFLICT (id_regiao) DO NOTHING;
        """

        for _, row in df.iterrows():
            cursor.execute(sql_insert, (
                row["id_regiao"],
                row["nome_regiao"]
            ))

        conn.commit()
        print("Dimensão Região carregada com sucesso!")

    except Exception as e:
        print(f"Erro ao carregar região: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()