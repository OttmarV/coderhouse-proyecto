FROM apache/airflow:2.6.2-python3.11 AS coderhouse-proyecto

WORKDIR /requirements

COPY requirements.txt ./

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

WORKDIR /src