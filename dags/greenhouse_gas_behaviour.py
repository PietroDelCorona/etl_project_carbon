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
        URL = "https://ourworldindata.org/grapher/per-capita-energy-stacked.csv?v=1&csvType=full&useColumnShortNames=true"

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

    def clean_co2_emission(source):
        try:
            file = s3.get_object(
                Bucket ='bronze',
                Key = f"co2_emissions/{source}"
            )

            co2_emissions_per_capita = pd.read_csv(file['Body'], sep=',')

            co2_emissions_per_capita = co2_emissions_per_capita.drop(columns=['Code'])

            csv_buffer = StringIO()
            co2_emissions_per_capita[['Entity', 'Year', 'emissions_total_per_capita']].to_csv(csv_buffer, index=False)

            s3.put_object(
                Body=csv_buffer.getvalue(),
                Bucket='silver',
                Key=f'co2_emissions/cleansed_{source}',
                ContentType = 'application/csv'
            )
            print(f"Arquivo {source} processado e salvo no bucket: 'silver' com sucesso!")
        except Exception as e:
            print(f"Erro ao processar o arquivo {source}: {e}")

    def clean_population_data(source):
        try:
            file = s3.get_object(
                Bucket ='bronze',
                Key = f"population/{source}"
            )

            world_population = pd.read_csv(file['Body'], sep=',', low_memory=False)

            world_population = world_population.drop(columns=['Record Type','Reliability','Source Year','Value Footnotes'])

            world_population = world_population.dropna(subset=['Value'])

            world_population = world_population[world_population["Sex"] == "Both Sexes"]

            world_population = world_population.drop(columns=['Sex'])

            csv_buffer = StringIO()
            world_population[['Country or Area', 'Year', 'Area', 'Value']].to_csv(csv_buffer, index=False)

            s3.put_object(
                Body=csv_buffer.getvalue(),
                Bucket='silver',
                Key=f'population/cleansed_{source}',
                ContentType = 'application/csv'
            )
            print(f"Arquivo {source} processado e salvo no bucket: 'silver' com sucesso!")          
        except Exception as e:
            print(f"Erro ao processar o arquivo {source}: {e}")

    def clean_energy_mix(source):
        try:
            file = s3.get_object(
                Bucket = 'bronze',
                Key = f'energy_mix/{source}'
            )
        
            energy_stacked_per_capita = pd.read_csv(file['Body'], sep=",")

            energy_stacked_per_capita = energy_stacked_per_capita.drop(columns=['Code'])

            energy_stacked_per_capita.fillna(0, inplace=True)

            # print(energy_stacked_per_capita.columns.tolist())

            csv_buffer = StringIO()
            energy_stacked_per_capita[['Entity','Code','Year', 'coal_per_capita__kwh', 'oil_per_capita__kwh', 'gas_per_capita__kwh', 'nuclear_per_capita__kwh__equivalent', 'hydro_per_capita__kwh__equivalent', 'wind_per_capita__kwh__equivalent', 'solar_per_capita__kwh__equivalent', 'other_renewables_per_capita__kwh__equivalent']].to_csv(csv_buffer, index=False)

            s3.put_object(
                Body = csv_buffer.getvalue(),
                Bucket = 'silver',
                Key = f"energy_mix/cleansed_{source}",
                ContentType = "application/csv"
            )
            print(f"Arquivo {source} processado e salvo no bucket: 'silver' com sucesso!")
        except Exception as e:
            print(f"Erro ao processar o arquivo {source}: {e}")

    def clean_co2_land_use(source):
        try:
            file = s3.get_object(
                Bucket ='bronze',
                Key = f"co2_land_use/{source}"
            )

            co2_land_use = pd.read_csv(file['Body'], sep=',')

            co2_land_use = co2_land_use.drop(columns=['Code'])

            co2_land_use = co2_land_use.dropna(subset=['emissions_from_land_use_change','emissions_total'])

            # print(co2_land_use.columns.tolist())

            csv_buffer = StringIO()
            co2_land_use[['Entity', 'Year', 'emissions_from_land_use_change', 'emissions_total']].to_csv(csv_buffer, index=False)

            s3.put_object(
                Body = csv_buffer.getvalue(),
                Bucket = 'silver',
                Key = f"co2_land_use/cleansed_{source}",
                ContentType = "application/csv"
            )
            print(f"Arquivo {source} processado e salvo no bucket: 'silver' com sucesso!")
        except Exception as e:
            print(f"Erro ao processar o arquivo {source}: {e}")

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
        python_callable=clean_co2_emission,
        op_kwargs = {"source" : "co2_emission_per_capita.csv"}
    )

    clean_population_task = PythonOperator(
        task_id = "clean_population_data",
        python_callable=clean_population_data,
        op_kwargs = {"source" : "world_population.csv"}
    )

    clean_energy_mix_task = PythonOperator(
        task_id = "clean_energy_mix",
        python_callable=clean_energy_mix,
        op_kwargs = {"source" : "energy_mix_sources.csv"}
    )

    clean_co2_land_use_task = PythonOperator(
        task_id = "clean_co2_land_use",
        python_callable=clean_co2_land_use,
        op_kwargs = {"source" : "co2_land_use.csv"}
    )

    
    get_co2_task >> get_population_task >> get_energy_mix >> get_co2_land_use >> clean_co2_emission_task >> clean_population_task >> clean_energy_mix_task >> clean_co2_land_use_task
    
    