import psycopg2 as pg

# Trocar a senha e outras informações


def get_connection():
    return pg.connect(
        host="localhost",
        database="ClamedMarketAnalysis",
        user="postgres",
        password="alinda"
    )
