import psycopg2

from connection import get_connection

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
            CREATE TABLE IF NOT EXISTS produtos (
                id_produto SERIAL PRIMARY KEY,
                cod_cean VARCHAR(20) NOT NULL,
                cod_prod VARCHAR(50),
                nome_produto VARCHAR(200) NOT NULL
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
                id_produto     INTEGER NOT NULL,
                volume_venda   NUMERIC(18,2) NOT NULL DEFAULT 0,
                periodo        DATE NOT NULL,

                CONSTRAINT pk_volume_vendas 
                    PRIMARY KEY (id_regiao, id_bandeira, id_produto, periodo),

                CONSTRAINT fk_volume_regiao
                    FOREIGN KEY (id_regiao) REFERENCES regiao(id_regiao),

                CONSTRAINT fk_volume_bandeira
                    FOREIGN KEY (id_bandeira) REFERENCES bandeira(id_bandeira),

                CONSTRAINT fk_volume_produto
                    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS vendas_filial_pp (
                id_filial     INTEGER NOT NULL,
                id_produto    INTEGER NOT NULL,
                volume_venda  NUMERIC(18,2) NOT NULL DEFAULT 0,
                periodo       DATE NOT NULL,

                CONSTRAINT pk_vendas_filial_pp 
                    PRIMARY KEY (id_filial, id_produto, periodo),

                CONSTRAINT fk_venda_filial
                    FOREIGN KEY (id_filial) REFERENCES filial(id_filial),

                CONSTRAINT fk_venda_produto
                    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
            );
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

if __name__ == "__main__":
    create_tables()