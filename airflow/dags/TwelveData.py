from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator


default_args = {
    "owner": "OttmarV",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

WKF_NAME = "twelve_data_stock"
WKF_DESCRIPTION = "Entregable 3 de proyecto CoderHouse DEF"
WKF_TAGS = ["coderhouse", "TwelveData", "TerceraEntrega"]

with DAG(
    dag_id=WKF_NAME,
    description=WKF_DESCRIPTION,
    schedule_interval="0 10 * * *",
    default_args=default_args,
    tags=WKF_TAGS,
    start_date=datetime(2023, 10, 22, 0),
) as dag:
    # Defaults Tasks:
    start_dag = DummyOperator(task_id="start_dag")
    end_dag = DummyOperator(task_id="end_dag")

    twelveData = BashOperator(
        task_id="twelve_data_etl",
        bash_command="python /src/main.py",
    )

    # twelveData = PythonOperator(
    #     task_id="twelve_data_etl",
    #     python_callable=,
    # )

    twelveData

    start_dag >> twelveData >> end_dag
