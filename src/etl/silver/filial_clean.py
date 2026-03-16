import pandas as pd
from src.etl.db.connection import get_connection

def silver_filial_transform():
    # 1. Inicia conexão e cursor
    conn = get_connection()
    cur = conn.cursor()

    # 2. Executa o TRUNCATE usando o CURSOR
    cur.execute("TRUNCATE TABLE silver.filial_clean")
    conn.commit() # Importante dar commit após o truncate

    # 3. Lê da Bronze usando o CURSOR (para evitar erro de read_sql)
    cur.execute("SELECT * FROM bronze.filial_raw")
    colunas = [desc[0] for desc in cur.description]
    dados = cur.fetchall()
    df = pd.DataFrame(dados, columns=colunas)

    if df.empty:
        print("Camada Bronze de filiais está vazia.")
        cur.close()
        conn.close()
        return

    # 4. Tratamentos (Seu código original de limpeza)
    df = df.rename(columns={
        "brick": "regiao",
        "cod_filial": "codigo_filial" # Ajustado para o nome que vem da Bronze
    })

    df["codigo_regiao"] = df["regiao"].astype(str).str.split(" - ").str[0]
    df["regiao"] = df["regiao"].str.replace(r"^\d+\s*-\s*", "", regex=True)

    # ... (Seu dicionário de replace de nomes de região entra aqui) ...
    # df["regiao"] = df["regiao"].replace({...})

    # 5. Salva na Silver linha por linha (Padrão Psycopg2)
    # Substituímos o to_sql para evitar o erro de 'sqlite_master'
    insert_query = """
        INSERT INTO silver.filial_clean (
            regiao, codigo_filial, codigo_regiao
        ) VALUES (%s, %s, %s)
    """

    for _, row in df.iterrows():
        cur.execute(insert_query, (
            row["regiao"],
            row["codigo_filial"],
            row["codigo_regiao"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    print("Dados inseridos na tabela silver.filial_clean com sucesso!")