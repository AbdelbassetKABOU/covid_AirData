# On importe les Operators dont nous avons besoin.
from pymongo import MongoClient
from csv import reader
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import json
import time
import pandas as pd

default_args = {
    'owner': 'airflow',
    'email': ['airflow@airflow.com'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Création du DAG
dag = DAG(
    'covid_dag',
    default_args=default_args,
    description='Airflow 101',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(2),
    tags=['exemple'],
)


t1 = BashOperator(
    task_id='extract',
    bash_command='curl -X GET "https://coronavirusapi-france.vercel.app/AllDataByDate?date=2020-04-19" > /opt/airflow/cellar/data.json; echo "bonjourrrrrr"; exit 99;',
    dag=dag
)

def transform(filename,**kwargs):
    time.sleep(5)
    with open(filename) as json_file:
        data = json.load(json_file)
    df = pd.io.json.json_normalize(data, record_path =['allFranceDataByDate'])
    df = df[['code','date','deces','gueris']]
    df.to_csv('/opt/airflow/cellar/data.csv')

t2 = PythonOperator(
        task_id='transform',
        python_callable=transform,
        op_kwargs={'filename': '/opt/airflow/cellar/data.json'},
        dag=dag,
    )


def load(filename,**kwargs):
    client = MongoClient(
        host='mongodb',
        port=27017
    )

    db = client["covid"]
    collection = db["result"]
    with open(filename, 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        if header != None:
            for row in csv_reader:
                collection.insert_one({"dep":row[1],"date":row[2],"deces":row[3],"gueris":row[4]})


t3 = PythonOperator(
    task_id='load',
    python_callable=load,
    op_kwargs={'filename': '/opt/airflow/cellar/data.csv'},
    dag=dag,
    )

t1 >> t2 >> t3 
