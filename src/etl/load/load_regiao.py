import pandas as pd
from src.etl.db.connection import get_connection

def load_regiao():
    print("🚀 Carregando Dimensão Região a partir da Silver...")
    
    conn = None # Inicializa para evitar erro no finally
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Busca os dados usando o nome correto da coluna (codigo_regiao)
        # Usamos 'AS' no SQL para garantir que o nome no DataFrame seja amigável
        query = """
            SELECT DISTINCT 
                codigo_regiao AS id_regiao, 
                'Região ' || codigo_regiao AS nome_regiao 
            FROM silver.filial_clean
        """
        cursor.execute(query)
        
        # Converte para DataFrame
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            print("⚠️ Tabela Silver de filiais está vazia.")
            return

        # 2. SQL de Inserção na Região (Camada Gold)
        sql_insert = """
            INSERT INTO gold.regiao (id_regiao, nome_regiao)
            VALUES (%s, %s)
            ON CONFLICT (id_regiao) DO NOTHING;
        """

        for _, row in df.iterrows():
            # Agora os nomes batem com o 'AS' que definimos na query
            cursor.execute(sql_insert, (
                row["id_regiao"],
                row["nome_regiao"]
            ))

        conn.commit()
        print("✅ Dimensão Região carregada com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao carregar região: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()