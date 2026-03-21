import pandas as pd
import numpy as np
from src.etl.db.connection import get_connection

def silver_market_sales_transform():
    # 1. Conexão pura psycopg2
    conn = get_connection()
    cur = conn.cursor()

    # 2. Leitura da Bronze (Agora trazendo a nova coluna 'periodo')
    cur.execute("SELECT * FROM bronze.market_sales_raw")
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=columns)

    if df.empty:
        print("Bronze vazia.")
        cur.close()
        conn.close()
        return

    # 3. Tratamentos
    df["nome_produto"] = None 
    # Extrai apenas o número do brick (ex: '1147 - JOINVILLE' vira '1147')
    df["cod_regiao"] = df["brick"].astype(str).str.split(" - ").str[0].str.strip()
    
    # Renomeando colunas
    df = df.rename(columns={
        "ean": "cod_ean",
        "si_conc_un": "si_conc_un",
        "so_conc_un": "so_conc_un",
        "pp_un": "pp_un"
    })

    # Preenchendo NaN com 0 nas colunas numéricas
    cols_numeric = ["si_conc_un", "so_conc_un", "pp_un"]
    df[cols_numeric] = df[cols_numeric].fillna(0)

    # 4. Carga na Silver (Truncate e Loop de Insert)
    try:
        cur.execute("TRUNCATE TABLE silver.market_sales_clean")
        
        # SQL de Inserção incluindo o campo 'periodo'
        insert_query = """
            INSERT INTO silver.market_sales_clean (
                cod_regiao, cod_ean, cod_prod_catarinense, 
                si_conc_un, so_conc_un, pp_un, nome_produto, periodo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, row in df.iterrows():
            cur.execute(insert_query, (
                row["cod_regiao"],
                row["cod_ean"],
                row["cod_prod_catarinense"],
                row["si_conc_un"],
                row["so_conc_un"],
                row["pp_un"],
                row["nome_produto"],
                row["periodo"]  # <--- Repassando o período vindo da Bronze
            ))

        conn.commit()
        print("✅ Dados processados e inseridos na silver.market_sales_clean com período!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro na carga Silver: {e}")
    finally:
        cur.close()
        conn.close()