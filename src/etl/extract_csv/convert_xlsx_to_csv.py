import os
import pandas as pd
import logging

logger = logging.getLogger("ETL_Extract_XLSX")

def convert_all_xlsx_in_folder(
    input_dir: str = "data/xlsx_raw",
    output_dir: str = "data/csv_raw"
):
    logger.info(f"Iniciando conversão de arquivos XLSX em: {input_dir}")
    
    if not os.path.exists(input_dir):
        logger.error(f"Diretório de entrada não encontrado: {input_dir}")
        return

    os.makedirs(output_dir, exist_ok=True)

    arquivos = [f for f in os.listdir(input_dir) if f.endswith(".xlsx")]
    
    if not arquivos:
        logger.warning(f"Nenhum arquivo .xlsx encontrado em {input_dir}")
        return

    logger.info(f"Total de arquivos encontrados para conversão: {len(arquivos)}")

    for file in arquivos:
        try:
            input_path = os.path.join(input_dir, file)
            filename = os.path.splitext(file)[0]
            output_path = os.path.join(output_dir, f"{filename}.csv")

            df = pd.read_excel(input_path)
            df.to_csv(output_path, index=False)

            logger.info(f"Sucesso: {file} -> {filename}.csv")

        except Exception as e:
            logger.error(f"Falha ao converter o arquivo {file}: {e}", exc_info=True)

    logger.info("Processo de conversão finalizado.")