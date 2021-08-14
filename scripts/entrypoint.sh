#!/usr/bin/env bash
pip install -r ./dags/requirements.txt
pip install pymongo
airflow db init
airflow users create -r Admin -u admin -e admin@example.com -f admin -l user -p admin
airflow webserver
