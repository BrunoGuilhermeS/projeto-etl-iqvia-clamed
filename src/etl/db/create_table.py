import psycopg2

from src.etl.db.connection import get_connection

# Função para criar as tabelas no banco de dados


def create_tables():

    commands = [
        """
            CREATE TABLE IF NOT EXISTS regiao (
                id_regiao SERIAL PRIMARY KEY,
                nome_regiao VARCHAR(100) NOT NULL
            );
            """,
        """
            CREATE TABLE IF NOT EXISTS bandeira (
                id_bandeira SERIAL PRIMARY KEY,
                nome_bandeira VARCHAR(100) NOT NULL,
                tipo_bandeira VARCHAR(50) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS filial (
                id_filial SERIAL PRIMARY KEY,
                nome_filial VARCHAR(150) NOT NULL,
                id_regiao INTEGER NOT NULL,
                CONSTRAINT fk_regiao
                    FOREIGN KEY (id_regiao)
                    REFERENCES regiao(id_regiao)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            );
            """,
        """
            CREATE TABLE IF NOT EXISTS volume_vendas (
                id_regiao      INTEGER NOT NULL,
                id_bandeira    INTEGER NOT NULL,
                sk_produto     INTEGER NOT NULL,
                volume_venda   NUMERIC(18,2) NOT NULL DEFAULT 0,
                periodo        DATE NOT NULL,

                CONSTRAINT pk_volume_vendas 
                    PRIMARY KEY (id_regiao, id_bandeira, sk_produto, periodo),

                CONSTRAINT fk_volume_regiao
                    FOREIGN KEY (id_regiao) REFERENCES regiao(id_regiao),

                CONSTRAINT fk_volume_bandeira
                    FOREIGN KEY (id_bandeira) REFERENCES bandeira(id_bandeira),

                CONSTRAINT fk_volume_produto
                    FOREIGN KEY (sk_produto) REFERENCES gold.produtos(sk_produto)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS vendas_filial_pp (
                id_filial     INTEGER NOT NULL,
                sk_produto    INTEGER NOT NULL,
                volume_venda  NUMERIC(18,2) NOT NULL DEFAULT 0,
                periodo       DATE NOT NULL,

                CONSTRAINT pk_vendas_filial_pp 
                    PRIMARY KEY (id_filial, sk_produto, periodo),

                CONSTRAINT fk_venda_filial
                    FOREIGN KEY (id_filial) REFERENCES filial(id_filial),

                CONSTRAINT fk_venda_produto
                    FOREIGN KEY (sk_produto) REFERENCES gold.produtos(sk_produto)
            );
            """,
            """
            CREATE SCHEMA IF NOT EXISTS bronze;
            """,

            """
            CREATE SCHEMA IF NOT EXISTS silver;
            """,

            """
            CREATE SCHEMA IF NOT EXISTS gold;
            """,

            """
            CREATE TABLE IF NOT EXISTS bronze.produtos_raw (
                id_produto_original INTEGER,
                cod_ean INTEGER,
                cod_prod_catarinense VARCHAR(50),
                nome_produto VARCHAR(200)
            );
            """,

            """
            CREATE TABLE IF NOT EXISTS silver.produtos_clean (
                id_produto_original INTEGER,
                cod_ean INTEGER,
                cod_prod_catarinense VARCHAR(50),
                nome_produto VARCHAR(200)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS gold.produtos (
                sk_produto SERIAL PRIMARY KEY,

                id_produto_original INTEGER NOT NULL,
                cod_ean INTEGER NOT NULL,
                cod_prod_catarinense VARCHAR(50),
                nome_produto VARCHAR(200) NOT NULL,

                data_inicio_validade DATE NOT NULL,
                data_fim_validade DATE,
                flag_ativo BOOLEAN DEFAULT TRUE
            );
            """,
            """
            CREATE UNIQUE INDEX idx_produto_ativo
                ON gold.produtos (id_produto_original)
                WHERE flag_ativo = TRUE;"""
            ,
            """
            CREATE TABLE IF NOT EXISTS bronze.filial_raw (
                brick TEXT,
                cod_filial INTEGER,
                data_ingestao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );""",
            """
            CREATE TABLE IF NOT EXISTS bronze.market_sales_raw (
            brick TEXT,
            ean BIGINT,
            cod_prod_catarinense INTEGER,
            si_conc_un NUMERIC,
            so_conc_un NUMERIC,
            pp_un NUMERIC,
            data_ingestao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
    ]

    try:
        conn = get_connection()
        cur = conn.cursor()

        for command in commands:
            cur.execute(command)

        conn.commit()
        cur.close()
        conn.close()
        print("Tabelas criadas com sucesso!")

    except psycopg2.Error as e:
        print("Erro ao criar tabelas:", e)


def create_comments():

    comments = [
        """
        COMMENT ON TABLE regiao IS 'Dimensão de regiões comerciais';

        COMMENT ON COLUMN regiao.id_regiao IS 'Chave primária da região';
        COMMENT ON COLUMN regiao.nome_regiao IS 'Nome da região comercial';
        """,
        """
            COMMENT ON TABLE bandeira IS 'Dimensão de bandeiras do mercado (própria, concorrente, PP)';

            COMMENT ON COLUMN bandeira.id_bandeira IS 'Identificador único da bandeira';
            COMMENT ON COLUMN bandeira.nome_bandeira IS 'Nome da bandeira comercial';
            COMMENT ON COLUMN bandeira.tipo_bandeira IS 'Classificação da bandeira (CLAMED, CONCORRENTE, PRECO POPULAR)';
        """,

        """
            COMMENT ON TABLE produtos IS 'Dimensão de produtos comercializados';

            COMMENT ON COLUMN produtos.sk_produto IS 'Identificador interno do produto';
            COMMENT ON COLUMN produtos.cod_ean IS 'Código EAN do produto';
            COMMENT ON COLUMN produtos.cod_prod_catarinense IS 'Código interno do produto na base Catarinense';
            COMMENT ON COLUMN produtos.nome_produto IS 'Descrição/nome comercial do produto';
        """,
        """
        COMMENT ON TABLE volume_vendas IS 'Fato de volume de vendas agregado por região, bandeira e produto';

        COMMENT ON COLUMN volume_vendas.id_regiao IS 'Região onde a venda ocorreu';
        COMMENT ON COLUMN volume_vendas.id_bandeira IS 'Bandeira associada à venda';
        COMMENT ON COLUMN volume_vendas.sk_produto IS 'Produto vendido';
        COMMENT ON COLUMN volume_vendas.volume_venda IS 'Quantidade vendida no período';
        COMMENT ON COLUMN volume_vendas.periodo IS 'Período de referência da venda (mês/ano)';
        """,
        """
        COMMENT ON TABLE vendas_filial_pp IS 'Fato de vendas por filial para bandeira Preço Popular';

        COMMENT ON COLUMN vendas_filial_pp.id_filial IS 'Identificador da filial';
        COMMENT ON COLUMN vendas_filial_pp.sk_produto IS 'Produto vendido na filial';
        COMMENT ON COLUMN vendas_filial_pp.volume_venda IS 'Quantidade vendida';
        COMMENT ON COLUMN vendas_filial_pp.periodo IS 'Período de referência da venda';
        """
    ]

    try:
        conn = get_connection()
        cur = conn.cursor()

        for comment in comments:
            cur.execute(comment)

        conn.commit()
        cur.close()
        conn.close()
        print("Comentários criados com sucesso!")

    except psycopg2.Error as e:
        print("Erro ao criar comentários:", e)


if __name__ == "__main__":
    create_tables()
    create_comments()
