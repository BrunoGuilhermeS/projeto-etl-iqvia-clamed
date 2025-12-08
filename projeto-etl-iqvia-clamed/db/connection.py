import psycopg2 as pg


def get_connection():
    return pg.connect(
        host="localhost",
        database ="ClamedMarketAnalysis",
        user ="postgres",
        password ="alinda"
    )
