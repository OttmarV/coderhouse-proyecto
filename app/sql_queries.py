# TEST QUERY
test_query = """select distinct(tablename) from pg_table_def
                where schemaname = 'ottmarfvv_coderhouse';"""

# DROP TABLES
landing_table_drop = "DROP TABLE IF EXISTS ottmarfvv_coderhouse.landing_stock_exchange;"

# CREATE TABLES
landing_table_create = """
CREATE TABLE IF NOT EXISTS ottmarfvv_coderhouse.landing_stock_exchange (
        datetime TIMESTAMP WITHOUT TIME ZONE ENCODE az64,
        symbol VARCHAR(50) ENCODE lzo,
        currency VARCHAR(50) ENCODE lzo,
        exchange_timezone VARCHAR(50) ENCODE lzo,
        exchange VARCHAR(50) ENCODE lzo,
        mic_code VARCHAR(50) ENCODE lzo,
        type VARCHAR(50) ENCODE lzo,
        price_open DECIMAL(10,2) ENCODE az64,
        price_high DECIMAL(10,2) ENCODE az64,
        price_low DECIMAL(10,2) ENCODE az64,
        price_close DECIMAL(10,2) ENCODE az64,
        volume BIGINT ENCODE az64,
        extraction_date_utc TIMESTAMP WITHOUT TIME ZONE ENCODE az64
) DISTSTYLE EVEN SORTKEY (datetime);
"""
