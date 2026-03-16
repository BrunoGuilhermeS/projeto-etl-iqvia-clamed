from src.etl.db.connection import get_connection
import pandas as pd
import os
import re


def load_volume_vendas():

    #caminho do csv limpo
    csv_path = os.path.join("data", "clean_datasets", "market_sales_12_2022.csv")

    # Extrai o período do nome do arquivo (ex: 12_2022 → 2022-12-01)
    match = re.search(r"(\d{2})_(\d{4})", csv_path)
    if match:
        mes = match.group(1)
        ano = match.group(2)
        periodo = f"{ano}-{mes}-01"
    else:
        periodo = "2022-12-01"

    print(f"Período detectado automaticamente: {periodo}")

    df = pd.read_csv(csv_path)

    #coluna bandeiras
    bandeiras_cols = ["PP_UN", "SO_CONC_UN", "SI_CONC_UN"]

    #mapeia as bandeiras pelo id_bandeira
    mapa_bandeiras = {
        "PP_UN": 1,
        "SO_CONC_UN": 2,
        "SI_CONC_UN": 3
    }

    #converte wide to long
    df_long = df.melt(
        id_vars=["cod_regiao", "cod_ean"],
        value_vars=bandeiras_cols,
        var_name="bandeira",
        value_name="volume_venda"
    )

    #remove zeros e NaN
    df_long = df_long[df_long["volume_venda"].notna()]
    df_long = df_long[df_long["volume_venda"] > 0]

    #converte para tipos padrão
    df_long["cod_regiao"] = df_long["cod_regiao"].astype(int)
    df_long["cod_ean"] = df_long["cod_ean"].astype(int)
    df_long["volume_venda"] = df_long["volume_venda"].astype(float)

    #mapeia id_bandeira
    df_long["id_bandeira"] = df_long["bandeira"].map(mapa_bandeiras)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        #SQL para buscar sk_produto
        sql_get_produto = """
            SELECT sk_produto 
            FROM gold.produtos 
            WHERE cod_ean = %s
            AND flag_ativo = TRUE
            """

        #SQL para inserir volume
        sql_insert = """
            INSERT INTO volume_vendas (id_regiao, id_bandeira, sk_produto, volume_venda, periodo)
            VALUES (%s, %s, %s, %s, %s)
        """

        for _, row in df_long.iterrows():

            #busca sk_produto
            cursor.execute(sql_get_produto, (row["cod_ean"],))
            result = cursor.fetchone()

            if result is None:
                print(f"[AVISO] Produto com EAN {row['cod_ean']} não encontrado. Pulando…")
                continue

            sk_produto = result[0]

            #executa no banco
            cursor.execute(sql_insert, (
                row["cod_regiao"],
                row["id_bandeira"],
                sk_produto,
                row["volume_venda"],
                periodo
            ))

        conn.commit()
        print("Volume de vendas carregado com sucesso!")

    except Exception as e:
        print("Erro ao inserir volume vendas:", e)

    finally:
        cursor.close()
        conn.close()

