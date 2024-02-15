from celery import Celery
from datetime import timedelta
import requests
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Celery configuration
app = Celery('tasks', broker='redis://localhost:6379/0')
app.conf.beat_schedule = {
    'update-database-daily': {
        'task': 'celery_app.update_database',
        'schedule': timedelta(seconds=int(os.getenv('SCHEDULE_TIME'))),
    },
}

@app.task
def update_database():
    headers = {'Authorization': f"Bearer {os.getenv('BEARER_TOKEN')}"}
    response = requests.get(os.getenv('API_URL'), headers=headers)
    data = response.json()

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
    )
    cur = conn.cursor()

    # Insert data into the table - Adjust the table name and columns as per your schema
    insert_query = 'INSERT INTO your_table_name (column1, column2) VALUES %s'
    execute_values(cur, insert_query, data)

    conn.commit()
    cur.close()
    conn.close()
