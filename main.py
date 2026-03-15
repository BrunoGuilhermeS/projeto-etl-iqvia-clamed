from src.etl.extract_csv.convert_xlsx_to_csv import convert_all_xlsx_in_folder
from src.etl.silver.filial_clean import silver_filial_transform
from src.etl.silver.market_sales_clean import extract_market_sales
from src.etl.load.load_regiao import load_regiao
from src.etl.load.load_produto import load_produto
from src.etl.load.load_filial import load_filial
from src.etl.load.load_bandeira import load_bandeira
from src.etl.load.load_volume_vendas import load_volume_vendas
from src.queries.queries import get_volume_vendas
from src.etl.db.create_table import create_tables, create_comments
from src.etl.bronze.load_raw_data import load_filial_raw, load_market_sales_raw

def main():
    print('Iniciando ETL')
    print('Extraindo dados das tabelas')
    convert_all_xlsx_in_folder()
    extract_market_sales("data/csv_raw/MS_12_2022_sample.csv")
    silver_filial_transform("data/csv_raw/filial-brick_sample.csv")

    print('Criando tabelas...')
    create_tables()

    print('Gerando comentários...')
    create_comments()

    print('Carregando regiões...')
    load_regiao()

    print('Carregando produtos...')
    load_produto()

    print('Carregando bandeiras...')
    load_bandeira()

    print('Carregando filiais...')
    load_filial()

    print('Carregando volume de vendas...')
    load_volume_vendas()

    df = get_volume_vendas()
    print(df.head(20))

    print('Pipeline executado com sucesso.')

if __name__ == "__main__":
    main()
