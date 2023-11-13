import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from airflow.models import Variable


def process_sql_result(**kwargs):
    ti = kwargs["ti"]
    sql_result = ti.xcom_pull(task_ids="compute_threshold")[0][0]
    ti.xcom_push(key="threshold_value", value=sql_result)

    if float(sql_result) < 130 or float(sql_result) > 150:
        return "send_email"
    return "end_dag"


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
