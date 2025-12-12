import pandas as pd
from src.etl.db.connection import get_connection


def dataframe():

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM volume_vendas", conn)

    print(df.head())

    return (df)
