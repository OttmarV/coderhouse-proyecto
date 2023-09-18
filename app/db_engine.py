import redshift_connector
from app.credentials import CREDS_REDSHIFT


def open_redshift_connection():
    conn = redshift_connector.connect(
        host=CREDS_REDSHIFT["HOST"],
        database=CREDS_REDSHIFT["DATABASE"],
        port=CREDS_REDSHIFT["PORT"],
        user=CREDS_REDSHIFT["USER"],
        password=CREDS_REDSHIFT["PASSWORD"],
    )

    return conn


def execute_query(conn, query, values: bool = False):
    cursor = conn.cursor()

    cursor.execute(query)

    if values:
        result: tuple = cursor.fetchall()
        return result


def close_redshift_connection(conn):
    conn.close()
