from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator

default_args = {
    "owner": "OttmarV",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# DAG Properties
WKF_NAME = "twelve_data_stock"
WKF_DESCRIPTION = "Entregable 3 de proyecto CoderHouse DEF"
WKF_TAGS = ["coderhouse", "TwelveData", "TerceraEntrega"]

with DAG(
    dag_id=WKF_NAME,
    description=WKF_DESCRIPTION,
    schedule_interval="@daily",
    default_args=default_args,
    tags=WKF_TAGS,
    start_date=datetime(2023, 10, 22, 0),
    template_searchpath=["/src/libs"],
    catchup=False,
    params={"stock": "AMZN", "start_date": "2020-01-01", "end_date": "2020-12-31"},
) as dag:
    # Defaults Tasks:
    start_dag = DummyOperator(task_id="start_dag")
    end_dag = DummyOperator(task_id="end_dag")

    twelveData = BashOperator(
        task_id="twelve_data_etl",
        bash_command="python /src/main.py",
    )

    # For amazon provider version 7.4.1
    avgThreshold = RedshiftSQLOperator(
        task_id="compute_threshold",
        sql="avg_threshold.sql",
        redshift_conn_id="redshift_default",
    )

    start_dag >> twelveData >> avgThreshold >> end_dag
