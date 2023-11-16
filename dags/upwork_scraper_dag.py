from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime,timedelta
from scraper.constant import transformed_data_insert_query,url_list
from scraper.upwork_scraper import main
from src.scrapper.stackoverflow import ScrapingDataFromStackOverFlow

def scrape_all_pages(arguments):
	for data in arguments:
		try:
			print(f"Task started for the search key {data[1]}")
			main(data[0],data[1])
			print(f"Task successful for the search key {data[1]}")
		except ValueError as e:
			print(f"Task failed for the search key {data[1]} with error: {e}")

	print("All tasks completed.")

def stack_overflow():
	storage = ScrapingDataFromStackOverFlow()
	storage.execute_scraping()
    

default_args = {
    'owner': 'stack_overflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 25, 13, 0),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
	dag_id="stack_overflow",
    default_args=default_args,
    description='DAG to run a task daily at 6:30 PM',
    schedule_interval='0 13 * * *',  # Schedule to run at 1 PM UTC time
    catchup=False,  # Prevent backfilling of previous dates
    max_active_runs=1,	
     ) as dag :

	scraping_data_from_stack_overflow = PythonOperator(
		task_id = 'stack_overflow',
		python_callable = stack_overflow,
		provide_context=True

	)
	scraping_data_from_stack_overflow
