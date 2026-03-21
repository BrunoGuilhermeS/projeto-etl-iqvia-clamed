import psycopg2 as pg
import pandas as pd
from src.etl.db.connection import get_connection
import os

def load_gold_produtos():
    # --- Configuração de Caminhos ---
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    csv_path = os.path.join(ROOT, "data", "clean_datasets", "market_sales_12_2022.csv")

    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo não encontrado em {csv_path}")
        return

    # --- Leitura e Preparação ---
    df = pd.read_csv(csv_path)
    
    # Selecionamos as colunas do CSV: 'pp_un' é o preço
    df_produtos = df[["cod_ean", "cod_prod_catarinense", "nome_produto", "PP_UN"]].drop_duplicates().copy()

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # SQL 1: Inativar registros se o NOME ou PREÇO (valor_produto) mudou
        # ⚠️ Note que comparamos a coluna da GOLD (valor_produto) com o parâmetro do Python (%s)
        update_sql = """
            UPDATE gold.produtos 
            SET flag_ativo = FALSE, 
                data_fim_validade = CURRENT_DATE 
            WHERE id_produto_original = %s 
              AND flag_ativo = TRUE 
              AND (valor_produto <> %s OR nome_produto <> %s);
        """

        # SQL 2: Inserir nova versão (apenas se não houver uma ativa agora)
        insert_sql = """
            INSERT INTO gold.produtos (
                id_produto_original,
                cod_ean,
                cod_prod_catarinense,
                nome_produto,
                valor_produto,
                data_inicio_validade,
                flag_ativo
            )
            SELECT %s, %s, %s, %s, %s, CURRENT_DATE, TRUE
            WHERE NOT EXISTS (
                SELECT 1 FROM gold.produtos 
                WHERE id_produto_original = %s AND flag_ativo = TRUE
            );
        """

        for _, row in df_produtos.iterrows():
            id_original = int(row['cod_ean'])
            valor_csv = float(row['PP_UN']) if not pd.isna(row['PP_UN']) else 0.0
            nome_prod = str(row['nome_produto'])
            cod_cat = str(int(row['cod_prod_catarinense'])) if not pd.isna(row["cod_prod_catarinense"]) else None

            # 1. Tenta expirar a versão antiga se algo mudou
            cursor.execute(update_sql, (id_original, valor_csv, nome_prod))
            
            # 2. Insere a nova versão (se o slot ficou vazio no passo acima ou se é produto novo)
            # Passamos os parâmetros na ordem: id_orig, ean, cat, nome, valor, id_orig_para_o_not_exists
            cursor.execute(insert_sql, (
                id_original, 
                id_original, 
                cod_cat, 
                nome_prod, 
                valor_csv, 
                id_original
            ))

        conn.commit()
        print("Carga Gold de Produtos (SCD Tipo 2) finalizada com sucesso!")

    except Exception as e:
        if conn:
            conn.commit() # Garante que não fiquem transações abertas em erro
        print(f"Erro ao carregar produtos: {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    load_gold_produtos()