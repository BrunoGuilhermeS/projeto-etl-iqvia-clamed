import pandas as pd
import pandas as pd
from src.etl.db.connection import get_connection


def silver_filial_transform(input_path: str,
                         output_path: str = "data/clean_datasets/filial_clean.csv"
                         ) -> None:
    # Lê o CSV
    df = pd.read_csv(input_path)

    # Corrige o nome das colunas
    df = df.rename(columns={
        "Unnamed: 0": "index",
        "brick": "regiao",
        "Cód. Filial": "codigo_filial"
    })

    # Cria a coluna com o código da região, e limpa o nome da região
    df["codigo_regiao"] = df["regiao"].astype(str).str.split(" - ").str[0]
    df["regiao"] = df["regiao"].str.replace(r"^\d+\s*-\s*", "", regex=True)

    # Arruma os nomes da região
    df["regiao"] = df["regiao"].replace({
        "S.J.RIO PRETO-CENTRO": "SAO JOSE DO RIO PRETO - CENTRO",
        "S.J.RIO PRETO-V.S.MANOEL": "SAO JOSE DO RIO PRETO - VILA SANTA MANOEL",
        "CHAC.SANTO ANTONIO": "CHACARA SANTO ANTONIO",
        "PRES.PRUDENTE": "PRESIDENTE PRUDENTE",
        "SE": "SE - SUDESTE",
        "C.GRANDE-V.ANT.VENDAS": "CAMPO GRANDE - VILA ANTÔNIO",
        "P.PUBLICO": "PARQUE PUBLICO",
        "S.JOSE DOS PINHAIS": "SAO JOSE DOS PINHAIS",
        "P.GROSSA/PALMEIRA": "PONTA GROSSA / PALMEIRA",
        "LOND.S.PEDRO I": "LONDRINA - SAO PEDRO I",
        "LOND S.NEVES": "LONDRINA - SANDRO NEVES",
        "TORORO-POLITEAMA": "TORORO - POLITEAMA",
        "ALTO GLORIA": "ALTO DA GLORIA",
        "ALTO RUA XV": "ALTO DA RUA XV",
        "S.FRANCISCO": "SAO FRANCISCO",
        "BIGORILHO": "BIGORRILHO",
        "UNIAO VITORIA": "UNIAO DA VITORIA",
        "NOVA STA ROSA": "NOVA SANTA ROSA",
        "LOND.IPIRANGA": "LONDRINA - IPIRANGA",
        "B.VISTA PARAISO": "BELA VISTA DO PARAISO",
        "FLOR.RODOVIARIA": "FLORIANOPOLIS - RODOVIARIA",
        "HOSP.CELSO RAMOS": "FLORIANOPOLIS - HOSPITAL CELSO RAMOS",
        "HOSP.CARIDADE": "FLORIANÓPOLIS - HOSPITAL CARIDADE",
        "BLUM.L.FREITAS": "BLUMENAU - LUIZ FREITAS",
        "BLUM.AMAZONAS": "BLUMENAU - AMAZONAS",
        "JOINV. - CENTRO": "JOINVILLE - CENTRO",
        "JOINV. - AMERICA": "JOINVILLE - AMERICA",
        "JOINV. - BAIRROS": "JOINVILLE - BAIRROS",
        "S.FRANCISCO SUL": "SAO FRANCISCO DO SUL",
        "S.MIGUEL D OESTE": "SAO MIGUEL DO OESTE",
        "DR.FLORES": "DOUTOR FLORES",
        "PORTO ALEGRA - CONCEICAO": "PORTO ALEGRE - VILA CONCEICAO",
        "POÇO DAS ANTAS": "POCO DAS ANTAS",
        "CAXIAS - S.VENDELINO": "CAIXAS - SAO VANDELINO",
        "PELOTAS - GAL.OSORIO": "PELOTAS - GENERAL OSORIO",
        "FARROPILHA": "FARROUPILHA",
        "L.VERMELHA": "LINHA VERMELHA",
        "STA.CRUZ DO SUL": "SANTA CRUZ DO SUL",
        "S.M.ACAMPAMENTO": "SANTA MARIA - ACAMPAMENTO",
    })

    # Configurações de exibição
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)

    # Salva o CSV limpo
    conn = get_connection()

    df.to_sql(
        name="filial_clean",
        con=conn,
        schema="silver",
        if_exists="append"
        index=False
    )

    conn.close()

    print("Dados inseridos na tabela silver.filial_clean")
