"""Contains the ETL pipeline to follow for TwelveData extraction 
"""

import os
import logging

from libs.api import TwelveData
from libs.sql_queries import landing_table_create, landing_table_drop
from libs.db_engine import (
    open_redshift_connection,
    execute_query,
    close_redshift_connection,
    upsert_records,
)

TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")


def main():
    """ETL Pipeline encapsulated in a function for importing purposes"""

    # Setup Logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("stock_app")

    # Initialize stock exchange object
    logger.info("Starting program\n")
    td = TwelveData(TWELVE_DATA_API_KEY)
    stock = ["AAPL", "AMZN", "DIS"]  # "ASR"

    # Get exchange data for the stock and date range requested
    logger.info(
        "Getting 2020 data from TwelveData API for %s stock(s)\n", (", ").join(stock)
    )
    exchange_data = td.get_exchange_data(stock, "2020-01-01", "2020-12-31")

    # Create a pandas dataframe out of the extracted data
    logger.info("Create a pandas DataFrame from data extracted\n")
    df = td.as_pandas(exchange_data)

    # Remove duplicates by primary keys
    logger.info("Removing duplicates by primary keys\n")
    df = td.remove_duplicates(df)

    # Write exchange data into a json file
    # logger.info("Creating json file from data extracted\n")
    # td.write_json(exchange_data)

    # Parse a json file into a python dictionary
    # logger.info("Reading json file into a python dictionary\n")
    # json_exchange_data = td.read_json("exchange_data.json")

    # Create connection to Redshift
    logger.info("Opening a redshift connection\n")
    conn = open_redshift_connection()

    # Drop landing table if exists
    # logger.info("Dropping landing table\n%s\n", landing_table_drop)
    # execute_query(conn, landing_table_drop)

    # Create landing table
    logger.info("Creating landing table\n%s\n", landing_table_create)
    execute_query(conn, landing_table_create)

    logger.info("Upserting landing table with dataframe data\n")
    upsert_records(conn, df)

    # Close redshift connection
    logger.info("Closing redshift connection\n")
    close_redshift_connection(conn)

    logger.info("End of script\n")


if __name__ == "__main__":
    main()
