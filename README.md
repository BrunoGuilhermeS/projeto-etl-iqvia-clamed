# projeto-etl-iqvia-clamed

Este projeto implementa um pipeline ETL (Extract, Transform, Load) utilizando Python, com o objetivo de extrair dados de vendas do mercado farmacêutico, realizar tratamento e padronização das informações e carregar os dados em um banco PostgreSQL para análises posteriores.

O projeto foi desenvolvido com foco em boas práticas de organização, separação de responsabilidades e análise exploratória de dados.

# Estrutura do Projeto

projeto-etl-iqvia-clamed/
│
├── data/
│   ├── xlsx_raw/           # Arquivos Excel brutos
│   ├── csv_raw/            # CSV extraídos
│   └── clean_datasets/     # Dados tratados
│
├── jupyter                 # Notebook com a validação dos dados
│
├── src/
│   ├── etl/
│   │   ├── extract_csv/    # Extrai os dados dos arquivos excel
│   │   ├── data_transform/ # Transforma os dados
│   │   ├── load/           # Carrega os dados no banco
│   │   └── db/             # Conector e criação das tabelas
│   └── queries/            # Consultas SQL para análise
│   
│
├── main.py                # Orquestrador do ETL
│
├──requirements.txt
└── README.md



# Tecnologias Utilizadas

Python 3.10+

Pandas

NumPy

PostgreSQL

psycopg2

Matplotlib

Jupyter Notebook


# Como funciona

- criar um banco de dados com o nome "ClamedMarketAnalysis", e/ou ajustar o arquivo "create_table.py" dentro de "src/etl/db"

- crie e rode a venv
    python -m venv .venv
    .venv\Scripts\Activate.ps1


- rode o requirements
    pip install -r requirements.txt

- rode o main
    python main.py

O script irá:

Extrair os dados brutos

Realizar o tratamento e padronização

Criar as tabelas no PostgreSQL

Carregar os dados para análise

# Observações

- Os dados tratados ficam disponíveis em data/clean_datasets

- As consultas de análise estão centralizadas em src/queries

- A tabela **vendas_filial** não é totalmente utilizada na versão atual do pipeline.
- Ela foi criada antecipadamente para suportar análises futuras em nível de filial, 
  permitindo a análise de como o desempenho de cada filial afeta a sua região.
  Essa estrutura evita retrabalho de modelagem quando novos datasets forem incorporados ao ETL.


