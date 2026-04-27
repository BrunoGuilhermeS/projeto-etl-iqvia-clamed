import logging
import os

def setup_logger():
    caminho_logs = "logs"
    os.makedirs(caminho_logs, exist_ok=True)

    arquivo_log = os.path.join(caminho_logs, "etl_pipeline.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(arquivo_log, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=== Sistema de Logs Inicializado ===")