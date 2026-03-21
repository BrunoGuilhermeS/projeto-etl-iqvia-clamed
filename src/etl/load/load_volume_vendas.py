import pandas as pd
from src.etl.db.connection import get_connection

def load_volume_vendas(): # <-- Removido o argumento 'periodo'
    print(f"🚀 Iniciando carga da Fato a partir da Silver (Período Automático)")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Busca os dados da camada Silver INCLUINDO a coluna periodo
        query_silver = """
            SELECT cod_regiao, cod_ean, si_conc_un, so_conc_un, pp_un, periodo 
            FROM silver.market_sales_clean
        """
        cursor.execute(query_silver)
        
        columns = [desc[0] for desc in cursor.description]
        df_silver = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df_silver.empty:
            print("⚠️ Camada Silver está vazia. Carga abortada.")
            return

        # 2. Mapeamento das bandeiras
        mapa_bandeiras = {
            "pp_un": 1,
            "so_conc_un": 2,
            "si_conc_un": 3
        }

        # 3. Wide to Long (Unpivot) - Mantemos o 'periodo' nos id_vars para não perdê-lo
        df_long = df_silver.melt(
            id_vars=["cod_regiao", "cod_ean", "periodo"], # <-- 'periodo' preservado aqui
            value_vars=["pp_un", "so_conc_un", "si_conc_un"],
            var_name="bandeira_col",
            value_name="volume_venda"
        )

        # Filtra volumes zerados ou nulos
        df_long = df_long[df_long["volume_venda"] > 0].dropna(subset=["volume_venda"])

        # 4. SQLs para busca de SK e Inserção
        sql_get_sk = """
            SELECT sk_produto FROM gold.produtos 
            WHERE id_produto_original = %s AND flag_ativo = TRUE
        """

        # IMPORTANTE: Adicionado o campo 'periodo' no INSERT e no VALUES
        sql_insert = """
            INSERT INTO gold.volume_vendas (id_regiao, id_bandeira, sk_produto, volume_venda, periodo)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT pk_volume_vendas 
            DO UPDATE SET volume_venda = EXCLUDED.volume_venda;
        """

        registros_inseridos = 0

        for _, row in df_long.iterrows():
            # Busca a SK ativa para o EAN
            cursor.execute(sql_get_sk, (int(row["cod_ean"]),))
            res = cursor.fetchone()

            if res:
                sk_produto = res[0]
                
                # Executa a inserção usando o row["periodo"] que veio da Silver
                cursor.execute(sql_insert, (
                    int(row["cod_regiao"]),
                    mapa_bandeiras[row["bandeira_col"]],
                    sk_produto,
                    float(row["volume_venda"]),
                    row["periodo"] # <-- Extraído diretamente da linha do DataFrame
                ))
                registros_inseridos += 1

        conn.commit()
        print(f"✅ Carga concluída! {registros_inseridos} registros processados automaticamente.")

    except Exception as e:
        print(f"❌ Erro na carga da Fato: {e}")
        if conn: conn.rollback()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()