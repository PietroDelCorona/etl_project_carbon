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
    
    def extract_co2_emission():
        pass

    def extract_population_data():
        pass

    def extract_energy_mix():
        pass

    def extract_co2_land_use():
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

    
    get_co2_task >> get_population_task >> get_energy_mix >> get_co2_land_use