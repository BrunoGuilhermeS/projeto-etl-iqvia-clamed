from src.etl.db.connection import get_connection
import pandas as pd
import os

def load_bandeira():
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_sql = """
        INSERT INTO bandeira (id_bandeira, nome_bandeira, tipo_bandeira)
        VALUES (1, 'Preco Popular', 'PP'),
        (2, 'Bandeiras Concorrentes SO', 'SO'),
        (3, 'Bandeiras Concorrente SI', 'SI');
        """

        cursor.execute (insert_sql)
        conn.commit()
        print("Bandeiras carregadas com sucesso!")
        
    except Exception as e:
        print("Erro ao inserir bandeira:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_bandeira()