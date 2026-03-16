import pandas as pd
import numpy as np
from src.etl.db.connection import get_connection

def silver_market_sales_transform():
    # 1. Conexão pura psycopg2
    conn = get_connection()
    cur = conn.cursor()

    # 2. Leitura da Bronze (usando o cursor para ler)
    # Como read_sql dá erro com psycopg2 puro, usamos o comando manual
    cur.execute("SELECT * FROM bronze.market_sales_raw")
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=columns)

    if df.empty:
        print("Bronze vazia.")
        cur.close()
        conn.close()
        return

    # 3. Tratamentos (Seus códigos de limpeza)
    df["nome_produto"] = None # No psycopg2, None vira NULL no banco
    df["cod_regiao"] = df["brick"].astype(str).str.split(" - ").str[0].str.strip()
    
    # Renomeando para bater com a Silver
    df = df.rename(columns={
        "ean": "cod_ean",
        "si_conc_un": "si_conc_un",
        "so_conc_un": "so_conc_un",
        "pp_un": "pp_un"
    })

    # Preenchendo NaN com 0
    cols_numeric = ["si_conc_un", "so_conc_un", "pp_un"]
    df[cols_numeric] = df[cols_numeric].fillna(0)

    # 4. Carga na Silver (Truncate e Loop de Insert)
    try:
        cur.execute("TRUNCATE TABLE silver.market_sales_clean")
        
        # SQL de Inserção
        insert_query = """
            INSERT INTO silver.market_sales_clean (
                cod_regiao, cod_ean, cod_prod_catarinense, 
                si_conc_un, so_conc_un, pp_un, nome_produto
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Executando a inserção para cada linha (padrão que você usou na Bronze)
        for _, row in df.iterrows():
            cur.execute(insert_query, (
                row["cod_regiao"],
                row["cod_ean"],
                row["cod_prod_catarinense"],
                row["si_conc_un"],
                row["so_conc_un"],
                row["pp_un"],
                row["nome_produto"]
            ))

        conn.commit()
        print("Dados processados e inseridos na silver.market_sales_clean!")

    except Exception as e:
        conn.rollback()
        print(f"Erro na carga Silver: {e}")
    finally:
        cur.close()
        conn.close()