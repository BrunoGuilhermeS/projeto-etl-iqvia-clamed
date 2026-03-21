from src.etl.db.connection import get_connection

def load_bandeira():
    print("🚀 Carregando Dimensão Bandeira...")
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # SQL de Inserção com valores estáticos (Regra de Negócio)
        # Usamos o ON CONFLICT para que o pipeline possa rodar várias vezes sem erro
        insert_sql = """
            INSERT INTO gold.bandeira (id_bandeira, nome_bandeira, tipo_bandeira)
            VALUES 
                (1, 'Preço Popular', 'PP'),
                (2, 'Bandeiras Concorrentes SO', 'SO'),
                (3, 'Bandeiras Concorrentes SI', 'SI')
            ON CONFLICT (id_bandeira) DO UPDATE SET 
                nome_bandeira = EXCLUDED.nome_bandeira,
                tipo_bandeira = EXCLUDED.tipo_bandeira;
        """

        cursor.execute(insert_sql)
        conn.commit()
        print("✅ Bandeiras carregadas/atualizadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inserir bandeira: {e}")
        if conn: conn.rollback()

    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    load_bandeira()