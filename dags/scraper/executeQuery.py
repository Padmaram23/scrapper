import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db_config = os.getenv('db_config')
HOST=os.getenv('HOST')
PORT=os.getenv('PORT')
USER=os.getenv('USER')
PASSWORD=os.getenv('PASSWORD')
DATABASE=os.getenv('DATABASE')

def insert_job_data(insertQuery,insertData):
    db_connection = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DATABASE
    )
    cursor = db_connection.cursor()

    cursor.executemany(insertQuery, insertData)
    db_connection.commit()

    # Close the connection
    cursor.close()
    db_connection.close()