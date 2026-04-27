import pandas as pd
import logging
from src.etl.db.connection import get_connection

logger = logging.getLogger("ETL_Silver_Filial")

def silver_filial_transform():
    conn = get_connection()
    cur = conn.cursor()

    try:
        logger.info("Iniciando a transformação da camada Silver (Filiais).")
        
        cur.execute("TRUNCATE TABLE silver.filial_clean")
        conn.commit()

        cur.execute("SELECT * FROM bronze.filial_raw")
        colunas = [desc[0] for desc in cur.description]
        dados = cur.fetchall()
        df = pd.DataFrame(dados, columns=colunas)

        if df.empty:
            logger.warning("Camada Bronze de filiais está vazia. Processo interrompido.")
            return

        df.columns = df.columns.str.strip()

        df = df.rename(columns={
            "brick": "regiao",
            "cod_filial": "codigo_filial",
            "Cód. Filial": "codigo_filial" 
        })

        mask_vazio = df["regiao"].isna() | (df["regiao"].astype(str).str.strip() == "") | (df["regiao"].astype(str).str.lower() == "nan")
        
        df.loc[mask_vazio, "regiao"] = "0 - SEM REGIAO"
        
        qtd_vazios = mask_vazio.sum()
        if qtd_vazios > 0:
            logger.info(f"Encontrados {qtd_vazios} registros sem região. Preenchidos com '0 - SEM REGIAO'.")

        df["codigo_regiao"] = df["regiao"].astype(str).str.split(" - ").str[0]
        
        df["regiao"] = df["regiao"].str.replace(r"^\d+\s*-\s*", "", regex=True).str.strip()

        mapeamento_nomes = {
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
        }
        
        df["regiao"] = df["regiao"].replace(mapeamento_nomes)

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
        logger.info(f"Sucesso! {len(df)} registros inseridos na tabela silver.filial_clean.")

    except Exception as e:
        logger.error(f"Erro durante a transformação da filial: {e}", exc_info=True)
        if conn:
            conn.rollback()
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if conn:
            conn.close()