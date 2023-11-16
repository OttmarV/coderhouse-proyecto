"""Utility functions to support main DAG"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from airflow.models import Variable


def process_sql_result(**kwargs: dict) -> str:
    """Callable that pushes the results of DAG threshold query

    Returns:
        str: Next node in dag
    """
    ti = kwargs["ti"]
    params = kwargs["params"]
    sql_result = float(ti.xcom_pull(task_ids="compute_threshold")[0][0])
    th_min = float(params.get("th_min"))
    th_max = float(params.get("th_max"))
    ti.xcom_push(key="threshold_value", value=sql_result)

    if sql_result < th_min or sql_result > th_max:
        return "send_email"
    return "end_dag"


def send_email_smtp(ti, **kwargs: dict) -> None:
    """Creates and sends email using smtplib library"""
    query_result = ti.xcom_pull(task_ids="process_result", key="threshold_value")
    params = kwargs["params"]
    stock = params.get("stock")
    start_date = params.get("start_date")
    th_min = params.get("th_min")
    th_max = params.get("th_max")
    end_date = params.get("end_date")

    with open("/opt/airflow/dags/utils/body.html", "r") as file:
        html = file.read().format(
            query_result=query_result,
            stock=stock,
            th_min=th_min,
            th_max=th_max,
            start_date=start_date,
            end_date=end_date,
        )

    smtp_server = Variable.get("SMTP_HOST_EMAIL")
    smtp_port = int(Variable.get("SMTP_PORT_EMAIL"))
    msg = MIMEMultipart()
    msg["From"] = Variable.get("SECRET_SMTP_EMAIL")
    msg["To"] = Variable.get("SECRET_SMTP_EMAIL")
    msg["Subject"] = "CODERHOUSE DAG TWELVE DATA THRESHOLD FAILURE"
    msg.attach(
        MIMEText(
            html,
            "html",
        )
    )
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(
            Variable.get("SECRET_SMTP_EMAIL"), Variable.get("SECRET_SMTP_PWD_EMAIL")
        )
        server.send_message(msg)
