from airflow import DAG
from airflow.operators.python import PythonOperator, get_current_context
from airflow.macros import ds_add
from os.path import join
import pendulum
import os
import boto3
import requests
import pandas as pd
from io import StringIO

with DAG(
    "greenhouse_gas_behaviour",
    description="Pipeline para ingestão e processamento de dados de emissões de CO2",
    schedule_interval="@daily",  
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
) as dag:

    s3 = boto3.client(
        's3',
        region_name='us-east-1',
        endpoint_url=os.environ.get('MINIO_ENDPOINT'),
        aws_access_key_id=os.environ.get('MINIO_ACCESS_KEY'),
        aws_secret_access_key =os.environ.get('MINIO_SECRET_KEY')
    )
    
    def extract_co2_emission():
        URL = "https://ourworldindata.org/grapher/co-emissions-per-capita.csv?v=1&csvType=full&useColumnShortNames=true"

        response = requests.get(URL, verify=False)

        if response.status_code == 200:

            filename = "co2_emission_per_capita.csv"

            s3.put_object(
                Body=response.text,
                Bucket='bronze',
                Key = f"co2_emissions/{filename}",
                ContentType = 'application/csv'
            )
            print(f"Arquivo {filename} enviado ao bucket: 'bronze' com sucesso!")
        else:
            print(f"Erro ao obter os dados: {response.status_code} - {response.text}")

    def extract_population_data():

        file_path = "./data/un_data_pop_world.csv"
    
        try:
            pop_world = pd.read_csv(file_path, sep=",")

            csv_buffer = StringIO()
            pop_world.to_csv(csv_buffer, index=False)

            filename = "world_population.csv"

            s3.put_object(
                Body = csv_buffer.getvalue(),
                Bucket = 'bronze',
                Key = f"population/{filename}",
                ContentType = "application/csv"
            )
            print(f"Arquivo {filename} enviado ao bucket: 'bronze' com sucesso!")
        except Exception as e:
            print(f"Erro ao processar o arquivo {file_path}: {e}")

    def extract_energy_mix():
        URL = "https://ourworldindata.org/grapher/per-capita-energy-source-stacked.csv?v=1&csvType=full&useColumnShortNames=true"

        response = requests.get(URL, verify=False)

        if response.status_code == 200:

            filename = "energy_mix_sources.csv"

            s3.put_object(
                Body = response.text,
                Bucket = 'bronze',
                Key = f"energy_mix/{filename}",
                ContentType = "application/csv"
            )
            print(f"Arquivo {filename} enviado ao bucket: 'bronze' com sucesso!")
        else:
            print(f"Erro ao obter os dados: {response.status_code} - {response.text}")


    def extract_co2_land_use():
        URL = "https://ourworldindata.org/grapher/co2-emissions-fossil-land.csv?v=1&csvType=full&useColumnShortNames=true"

        response = requests.get(URL, verify=False)

        if response.status_code == 200:

            filename = "co2_land_use.csv"

            s3.put_object(
                Body = response.text,
                Bucket = 'bronze',
                Key = f"co2_land_use/{filename}",
                ContentType = "application/csv"
            )
            print(f"Arquivo {filename} enviado ao bucket: 'bronze' enviado com sucesso!")
        else:
            print(f"Erro ao obter os dados: {response.status_code} - {response.text}")

    def clean_co2_emission():
        pass

    def clean_population_data():
        pass

    def clean_energy_mix():
        pass

    def clean_co2_land_use():
        pass

    get_co2_task = PythonOperator(
        task_id = "extract_co2_emission",
        python_callable=extract_co2_emission
    )

    get_population_task = PythonOperator(
        task_id = "extract_population_data",
        python_callable=extract_population_data
    )

    get_energy_mix = PythonOperator(
        task_id = "extract_energy_mix",
        python_callable=extract_energy_mix
    )

    get_co2_land_use = PythonOperator(
        task_id = "extract_co2_land_use",
        python_callable=extract_co2_land_use
    )

    clean_co2_emission_task = PythonOperator(
        task_id = "clean_co2_emission",
        python_callable=clean_co2_emission
    )

    clean_population_task = PythonOperator(
        task_id = "clean_population_data",
        python_callable=clean_population_data
    )

    clean_energy_mix_task = PythonOperator(
        task_id = "clean_energy_mix",
        python_callable=clean_energy_mix
    )

    clean_co2_land_use_task = PythonOperator(
        task_id = "clean_co2_land_use",
        python_callable=clean_co2_land_use
    )

    
    get_co2_task >> get_population_task >> get_energy_mix >> get_co2_land_use >> clean_co2_emission_task >> clean_population_task >> clean_energy_mix_task >> clean_co2_land_use_task
    
    