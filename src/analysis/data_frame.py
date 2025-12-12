import pandas as pd
from src.etl.db.connection import get_connection


def get_volume_vendas():

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM volume_vendas", conn)

    return (df)
