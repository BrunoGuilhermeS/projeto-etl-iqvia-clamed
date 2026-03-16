from pathlib import Path

from src.etl.extract_csv.convert_xlsx_to_csv import convert_all_xlsx_in_folder
from src.etl.silver.filial_clean import silver_filial_transform
from src.etl.silver.market_sales_clean import silver_market_sales_transform

from src.etl.load.load_regiao import load_regiao
from src.etl.load.load_produto import load_produto
from src.etl.load.load_filial import load_filial
from src.etl.load.load_bandeira import load_bandeira
from src.etl.load.load_volume_vendas import load_volume_vendas

from src.queries.queries import get_volume_vendas

from src.etl.db.create_table import create_tables, create_comments
from src.etl.bronze.load_raw_data import load_filial_raw, load_market_sales_raw


BASE_DIR = Path(__file__).resolve().parent


def main():

    print("Iniciando pipeline ETL")

    print("Criando tabelas...")
    create_tables()

    print("Criando comentários...")
    create_comments()

    print("Convertendo arquivos XLSX...")
    convert_all_xlsx_in_folder()

    print("Carregando dados raw na Bronze...")
    load_filial_raw(BASE_DIR / "data/csv_raw/filial-brick_sample.csv")
    load_market_sales_raw(BASE_DIR / "data/csv_raw/MS_12_2022_sample.csv")

    print("Processando camada Silver...")
    silver_market_sales_transform()
    silver_filial_transform()

    print("Carregando dimensões...")
    load_regiao()
    load_produto()
    load_bandeira()
    load_filial()

    print("Carregando fato de vendas...")
    load_volume_vendas()

    print("Executando consulta final...")
    df = get_volume_vendas()
    print(df.head(20))

    print("Pipeline executado com sucesso.")


if __name__ == "__main__":
    main()