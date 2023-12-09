from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.decorators import dag

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='sf_fires_dag',
    default_args=default_args,
    description='Airflow DAG for San Fransisco Fire Incidents Kafka streaming project',
    schedule_interval=timedelta(days=1),
)

task_start_import = BashOperator(
    task_id='start_import',
    bash_command='python3 import_fire_data.py',
    dag=dag,
)

task_run_producer = BashOperator(
    task_id='run_producer',
    bash_command='python3 KafkaProducer.py',
    dag=dag,
)

task_run_consumer = BashOperator(
    task_id='run_consumer',
    bash_command='python3 KafkaConsumer.py',
    dag=dag,
)

task_start_import >> task_run_producer
task_start_import >> task_run_consumer