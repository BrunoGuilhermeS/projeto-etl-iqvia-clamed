import logging
from pathlib import Path

from src.etl.extract_csv.convert_xlsx_to_csv import convert_all_xlsx_in_folder
from src.etl.silver.filial_clean import silver_filial_transform
from src.etl.silver.market_sales_clean import silver_market_sales_transform

from src.etl.load.load_regiao import load_regiao
from src.etl.load.load_gold_produto import load_gold_produtos
from src.etl.load.load_filial import load_filial
from src.etl.load.load_bandeira import load_bandeira
from src.etl.load.load_volume_vendas import load_volume_vendas

from src.queries.queries import get_volume_vendas

from src.etl.db.create_table import create_tables, create_comments
from src.etl.bronze.load_raw_data import load_filial_raw, load_market_sales_raw

from src.etl.log_config import setup_logger

BASE_DIR = Path(__file__).resolve().parent

def main():
    # Inicializa a configuração do arquivo de logs para todo o projeto
    setup_logger()
    logger = logging.getLogger("ETL_Orquestrador")

    try:
        logger.info("=== Iniciando pipeline ETL Completo ===")

        logger.info("Passo 1/7: Criando tabelas...")
        create_tables()

        logger.info("Passo 2/7: Criando comentários (documentação no banco)...")
        create_comments()

        logger.info("Passo 3/7: Convertendo arquivos XLSX para CSV...")
        convert_all_xlsx_in_folder()

        logger.info("Passo 4/7: Carregando dados raw na camada Bronze...")
        load_filial_raw(BASE_DIR / "data/csv_raw/filial-brick_sample.csv")
        load_market_sales_raw(BASE_DIR / "data/csv_raw/MS_12_2022_sample.csv")

        logger.info("Passo 5/7: Processando dados para a camada Silver...")
        silver_market_sales_transform()
        silver_filial_transform()

        logger.info("Passo 6/7: Carregando Dimensões (Gold)...")
        load_regiao()
        load_gold_produtos()
        load_bandeira()
        load_filial()

        logger.info("Passo 7/7: Carregando Tabela Fato (Gold)...")
        load_volume_vendas()

        logger.info("Executando consulta final de validação...")
        df = get_volume_vendas()
        
        # Como o DataFrame pode ser grande, podemos printar no console 
        # mas também registrar no log que a consulta foi feita
        print(df.head(20))
        logger.info(f"Consulta final retornou {len(df)} registros. Amostra exibida no console.")

        logger.info("=== Pipeline ETL finalizado com sucesso! ===")
        
    except Exception as e:
        logger.critical(f"Pipeline interrompido por erro fatal: {e}", exc_info=True)

if __name__ == "__main__":
    main()