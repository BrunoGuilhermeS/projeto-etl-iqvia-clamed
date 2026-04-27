# projeto-etl-iqvia-clamed

Este projeto implementa um pipeline ETL (Extract, Transform, Load) utilizando Python, com o objetivo de extrair dados de vendas do mercado farmacêutico, realizar o tratamento e a padronização das informações e carregar os dados em um banco de dados PostgreSQL utilizando a Arquitetura Medalhão (Bronze, Silver e Gold) para análises posteriores.

O projeto foi desenvolvido com foco em boas práticas de Engenharia de Dados, organização de código, rastreabilidade (logs) e separação de responsabilidades.

A análise foi baseada estritamente nos dados disponíveis na fonte bruta (Bronze Layer) para garantir a integridade dos resultados. Inferir preços sem uma base transacional real introduziria vieses e reduziria a confiabilidade estatística do pipeline.

O volume de unidades vendidas é o indicador primário de demanda e penetração de mercado. Ele permite identificar o comportamento do consumidor e a performance regional sem as distorções causadas por políticas de preços variáveis ou variações tributárias entre estados.

A arquitetura foi desenhada para ser modular. Embora o escopo atual foque em volume (conforme fornecido), o modelo de dados na camada Gold permite a inclusão de dimensões financeiras e métricas de faturamento (Revenue) de forma incremental, assim que novas fontes de dados forem integradas

# Estrutura do Projeto

projeto-etl-iqvia-clamed/
│
├── data/
│   ├── xlsx_raw/           # Arquivos Excel originais brutos
│   ├── csv_raw/            # Arquivos CSV convertidos e extraídos
│   └── clean_datasets/     # Datasets tratados exportados (backup/validação)
│
├── logs/                   # Arquivos de log gerados automaticamente pelo pipeline
│
├── jupyter/                # Notebooks com análises exploratórias e validação de dados
│
├── src/
│   ├── etl/
│   │   ├── extract_csv/    # Scripts de conversão (XLSX -> CSV)
│   │   ├── bronze/         # Ingestão de dados brutos na camada Bronze (Raw)
│   │   ├── silver/         # Limpeza e padronização na camada Silver (Clean)
│   │   ├── load/           # Carga nas Dimensões e Fatos na camada Gold (Business)
│   │   ├── db/             # Conexão com o banco, DDL (criação de tabelas) e comentários
│   │   └── log_config.py   # Configuração centralizada do sistema de monitoramento
│   └── queries/            # Consultas SQL para análise e validação de negócio
│
├── main.py                 # Orquestrador principal do pipeline ETL
├── requirements.txt        # Dependências e bibliotecas do projeto
└── README.md               # Documentação oficial



# Tecnologias Utilizadas

Linguagem: Python 3.10+

Manipulação de Dados: Pandas, NumPy

Banco de Dados: PostgreSQL, psycopg2

Monitoramento: Biblioteca nativa logging

Análise Exploratória: Jupyter Notebook, Matplotlib


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

- Rastreabilidade: Caso ocorra alguma falha na execução, consulte o arquivo de log gerado na pasta logs/ para obter a stack trace do erro e a etapa exata em que o pipeline parou.

- Consultas Prontas: As consultas de análise para extração de insights do banco estão centralizadas na pasta src/queries/.

- Escalabilidade (Tabela vendas_filial): Esta tabela não é totalmente utilizada na versão atual do pipeline de relatórios. Ela foi arquitetada de forma antecipada para suportar análises futuras em nível de filial (cruzamento de desempenho de filial vs. região), evitando retrabalho de modelagem de dados quando novos datasets mais granulares forem incorporados.

