import logging
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Gold_Bandeira")

def load_bandeira():
    logger.info("Iniciando o carregamento da dimensão Bandeira...")
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

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
        logger.info("Dimensão Bandeira carregada/atualizada com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro crítico ao carregar dimensão bandeira: {e}", exc_info=True)
        if conn: 
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Conexão com o banco encerrada.")

if __name__ == "__main__":
    load_bandeira()