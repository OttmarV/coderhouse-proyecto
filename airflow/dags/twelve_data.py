"""Set up TwelveData DAG, this includes ETL, Threshold check and email alert if required"""


from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator

from utils.functions import process_sql_result, send_email_smtp

# Setting up DAG default args
default_args = {
    "owner": "OttmarV",
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
    "conn_id": "redshift_default",
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
    params={
        "stock": "AMZN",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "th_min": 130,
        "th_max": 150,
    },
) as dag:
    # Start Node, representative start
    start_dag = DummyOperator(task_id="start_dag")

    # Execute ETL
    twelve_data_etl = BashOperator(
        task_id="twelve_data_etl",
        bash_command="python /src/main.py",
    )

    # For amazon provider version 7.4.1
    # Execute threshold query
    compute_threshold = RedshiftSQLOperator(
        task_id="compute_threshold",
        sql="avg_threshold.sql",
        wait_for_downstream=True,
        show_return_value_in_logs=True,
        redshift_conn_id="redshift_default",
    )

    # Process threshold query result and decides next node
    process_result = BranchPythonOperator(
        task_id="process_result",
        python_callable=process_sql_result,
        provide_context=True,
        wait_for_downstream=True,
    )

    # If threshold is not met, send email alert to user
    send_email = PythonOperator(
        task_id="send_email",
        python_callable=send_email_smtp,
        provide_context=True,
        wait_for_downstream=True,
    )

    # If threshold is met, end DAG
    end_dag = DummyOperator(
        task_id="end_dag",
        trigger_rule=TriggerRule.NONE_FAILED_OR_SKIPPED,
        wait_for_downstream=True,
    )

    # DAG sequence including branching
    start_dag >> twelve_data_etl >> compute_threshold >> process_result >> end_dag
    (
        start_dag
        >> twelve_data_etl
        >> compute_threshold
        >> process_result
        >> send_email
        >> end_dag
    )
