from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime,timedelta
from scraper.constant import transformed_data_insert_query,url_list
from scraper.upwork_scraper import main

    	
def scrape_all_pages(arguments):
	for data in arguments:
		try:
			print(f"Task started for the search key {data[1]}")
			main(data[0],data[1])
			print(f"Task successful for the search key {data[1]}")
		except ValueError as e:
			print(f"Task failed for the search key {data[1]} with error: {e}")

	print("All tasks completed.")


with DAG(
    dag_id='upwork_scrape_prod',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023,10,17)
     ) as dag :

	scraper = PythonOperator(
		task_id='scraper',
		python_callable=scrape_all_pages,
		op_args=[url_list],
		dag=dag
	)
	
	transformed_data_insert = SQLExecuteQueryOperator(
		task_id='transformed_data_insert',
		conn_id='upwork_prod_db',
		sql=transformed_data_insert_query,
		dag=dag
	)

	scraper >> transformed_data_insert