import os
import redshift_connector
import awswrangler as wr

CREDS_REDSHIFT_HOST = os.environ.get("CREDS_REDSHIFT_HOST")
CREDS_REDSHIFT_DATABASE = os.environ.get("CREDS_REDSHIFT_DATABASE")
CREDS_REDSHIFT_PORT = int(os.environ.get("CREDS_REDSHIFT_PORT"))
CREDS_REDSHIFT_USER = os.environ.get("CREDS_REDSHIFT_USER")
CREDS_REDSHIFT_PASSWORD = os.environ.get("CREDS_REDSHIFT_PASSWORD")


def open_redshift_connection():
    conn = redshift_connector.connect(
        host=CREDS_REDSHIFT_HOST,
        database=CREDS_REDSHIFT_DATABASE,
        port=CREDS_REDSHIFT_PORT,
        user=CREDS_REDSHIFT_USER,
        password=CREDS_REDSHIFT_PASSWORD,
    )

    conn.autocommit = True

    return conn


def execute_query(conn, query, values: bool = False):
    cursor = conn.cursor()

    cursor.execute(query)

    if values:
        result: tuple = cursor.fetchall()
        return result


def close_redshift_connection(conn):
    conn.close()


def upsert_records(conn, df):
    wr.redshift.to_sql(
        df=df,
        con=conn,
        schema="ottmarfvv_coderhouse",
        table="landing_stock_exchange",
        mode="upsert",
        primary_keys=["datetime", "symbol"],
        use_column_names=True,
    )
