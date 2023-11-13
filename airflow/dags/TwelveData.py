from datetime import datetime, timedelta

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator

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
    params={"stock": "AMZN", "start_date": "2020-01-01", "end_date": "2020-12-31"},
) as dag:
    # Defaults Tasks:
    start_dag = DummyOperator(task_id="start_dag")

    twelve_data_etl = BashOperator(
        task_id="twelve_data_etl",
        bash_command="python /src/main.py",
    )

    # For amazon provider version 7.4.1
    compute_threshold = RedshiftSQLOperator(
        task_id="compute_threshold",
        sql="avg_threshold.sql",
        wait_for_downstream=True,
        show_return_value_in_logs=True,
        redshift_conn_id="redshift_default",
    )

    def process_sql_result(**kwargs):
        ti = kwargs["ti"]
        sql_result = ti.xcom_pull(task_ids="compute_threshold")[0][0]
        ti.xcom_push(key="threshold_value", value=sql_result)

        if float(sql_result) < 130 or float(sql_result) > 150:
            return "send_email"
        return "end_dag"

    process_result = BranchPythonOperator(
        task_id="process_result",
        python_callable=process_sql_result,
        provide_context=True,
        wait_for_downstream=True,
    )

    def send_email_smtp(ti, **kwargs):
        query_result = ti.xcom_pull(task_ids="process_result", key="threshold_value")
        params = kwargs["params"]
        stock = params.get("stock")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        smtp_server = "smtp.office365.com"
        smtp_port = 587
        msg = MIMEMultipart()
        msg["From"] = Variable.get("SECRET_EMAIL")
        msg["To"] = Variable.get("SECRET_EMAIL")
        msg["Subject"] = "CODERHOUSE DAG TWELVE DATA THRESHOLD FAILURE"
        msg.attach(
            MIMEText(
                f"""<b><h1> Average value outside threshold limits for {stock} in date range {start_date} to {end_date} </h1></b>
                <b><h2> Vaule: {query_result} </h2></b>
                """,
                "html",
            )
        )
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(Variable.get("SECRET_EMAIL"), Variable.get("SECRET_PWD_EMAIL"))
            server.send_message(msg)
        print("El email fue enviado correctamente.")

    send_email = PythonOperator(
        task_id="send_email",
        python_callable=send_email_smtp,
        provide_context=True,
        wait_for_downstream=True,
    )

    end_dag = DummyOperator(
        task_id="end_dag",
        trigger_rule=TriggerRule.NONE_FAILED_OR_SKIPPED,
        wait_for_downstream=True,
    )

    start_dag >> twelve_data_etl >> compute_threshold >> process_result >> end_dag
    (
        start_dag
        >> twelve_data_etl
        >> compute_threshold
        >> process_result
        >> send_email
        >> end_dag
    )
