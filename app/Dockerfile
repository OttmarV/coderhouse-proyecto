FROM apache/airflow:2.6.2-python3.11

WORKDIR /src

COPY ./libs ./libs

COPY credentials.py main.py requirements.txt ./

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt