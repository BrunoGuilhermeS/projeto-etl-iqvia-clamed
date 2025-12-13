import pandas as pd
import numpy as np
import os


def extract_market_sales(input_path: str,
                         output_path: str = "data/clean_datasets/market_sales_12_2022.csv") -> None:
    """
    Extrai e trata o arquivo de vendas de mercado (IQVIA / concorrentes)
    e salva o CSV limpo para análise e carga no banco.
    """

    df = pd.read_csv(input_path)

    # Corrigindo nome das colunas
    df = df.rename(columns={
        "BRICK": "cod_regiao",
        "EAN": "cod_ean",
        "Cod Prod Catarinense": "cod_prod_catarinense",
        "Tipo Informacao SI Bandeira CONCORRENTE Unidade": "SI_CONC_UN",
        "Tipo Informacao SO Bandeira CONCORRENTE Unidade": "SO_CONC_UN",
        "Tipo Informacao SO Bandeira PRECO POPULAR Unidade": "PP_UN"
    })

    # Criando coluna de nome do produto (futuro enrichment)
    df["nome_produto"] = np.nan

    # Normalizando código da região
    df["cod_regiao"] = (
        df["cod_regiao"]
        .astype(str)
        .str.split(" - ")
        .str[0]
        .str.replace(" ", "")
    )

    # Preenchendo NaN com 0
    df["SI_CONC_UN"] = df["SI_CONC_UN"].fillna(0)
    df["SO_CONC_UN"] = df["SO_CONC_UN"].fillna(0)
    df["PP_UN"] = df["PP_UN"].fillna(0)

    # Garantindo pasta de saída
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Salvando CSV tratado
    df.to_csv(output_path, index=False)

    print("Arquivo market_sales tratado com sucesso!")
