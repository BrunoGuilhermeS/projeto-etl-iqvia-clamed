import pandas as pd
import logging
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Gold_Fato_VolumeVendas")

def load_volume_vendas():
    logger.info("Iniciando carga da Fato (Volume Vendas) a partir da Silver (Período Automático)...")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        logger.info("Buscando dados consolidados na camada Silver...")
        query_silver = """
            SELECT cod_regiao, cod_ean, si_conc_un, so_conc_un, pp_un, periodo 
            FROM silver.market_sales_clean
        """
        cursor.execute(query_silver)
        
        columns = [desc[0] for desc in cursor.description]
        df_silver = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df_silver.empty:
            logger.warning("Camada Silver está vazia. Carga da Fato abortada.")
            return

        logger.info(f"{len(df_silver)} registros recuperados da Silver. Aplicando unpivot (melt)...")

        mapa_bandeiras = {
            "pp_un": 1,
            "so_conc_un": 2,
            "si_conc_un": 3
        }

        df_long = df_silver.melt(
            id_vars=["cod_regiao", "cod_ean", "periodo"],
            value_vars=["pp_un", "so_conc_un", "si_conc_un"],
            var_name="bandeira_col",
            value_name="volume_venda"
        )

        df_long = df_long[df_long["volume_venda"] > 0].dropna(subset=["volume_venda"])
        logger.info(f"Transformação concluída. {len(df_long)} ocorrências de vendas válidas identificadas.")

        sql_get_sk = """
            SELECT sk_produto FROM gold.produtos 
            WHERE id_produto_original = %s AND flag_ativo = TRUE
        """
        
        sql_insert = """
            INSERT INTO gold.volume_vendas (id_regiao, id_bandeira, sk_produto, volume_venda, periodo)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT pk_volume_vendas 
            DO UPDATE SET volume_venda = EXCLUDED.volume_venda;
        """

        registros_inseridos = 0
        produtos_nao_encontrados = set()

        # 4. Inserção
        logger.info("Iniciando inserção no banco de dados (isso pode levar alguns instantes)...")
        for _, row in df_long.iterrows():
            ean_atual = int(row["cod_ean"])
            
            cursor.execute(sql_get_sk, (ean_atual,))
            res = cursor.fetchone()

            if res:
                sk_produto = res[0]
                
                cursor.execute(sql_insert, (
                    int(row["cod_regiao"]),
                    mapa_bandeiras[row["bandeira_col"]],
                    sk_produto,
                    float(row["volume_venda"]),
                    row["periodo"]
                ))
                registros_inseridos += 1
            else:
                produtos_nao_encontrados.add(ean_atual)

        conn.commit()
        logger.info(f"Carga da Fato concluída com sucesso! {registros_inseridos} registros processados e salvos.")

        if produtos_nao_encontrados:
            logger.warning(f"Atenção: {len(produtos_nao_encontrados)} produtos (EANs) não possuíam cadastro ativo na Dimensão Produtos e foram ignorados nesta carga.")

    except Exception as e:
        logger.error(f"Erro crítico na carga da Tabela Fato: {e}", exc_info=True)
        if conn: 
            conn.rollback()
    finally:
        if cursor: 
            cursor.close()
        if conn: 
            conn.close()
        logger.info("Conexão com o banco encerrada.")

if __name__ == "__main__":
    load_volume_vendas()