FROM apache/airflow:2.10.2
ADD requirements.txt .
RUN pip install -r requirements.txt