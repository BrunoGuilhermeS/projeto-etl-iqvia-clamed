from src.etl.extract_csv.convert_xlsx_to_csv import convert_all_xlsx_in_folder
from src.etl.data_transform.filial_clean import extract_filial_brick
from src.etl.data_transform.market_sales_clean import extract_market_sales
from src.etl.load.load_regiao import load_regiao
from src.etl.load.load_produto import load_produto
from src.etl.load.load_filial import load_filial
from src.etl.load.load_bandeira import load_bandeira
from src.etl.load.load_volume_vendas import load_volume_vendas
from src.queries.queries import get_volume_vendas
from src.etl.db.create_table import create_tables, create_comments


def main():
    print('Iniciando ETL')
    print('Extraindo dados das tabelas')
    convert_all_xlsx_in_folder()
    extract_market_sales("data/csv_raw/MS_12_2022_sample.csv")
    extract_filial_brick("data/csv_raw/filial-brick_sample.csv")

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


if __name__ == "__main__":
    main()
