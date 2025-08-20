import psycopg2
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import os
import json


with open('stocks.json') as f:
        SYMBOLS = json.load(f)
        
DB_CONFIG = {
    'dbname': 'AlgoMinds',
    'user': 'algominds',
    'password': 'machinedatabase',
    'host': 'localhost',
    'port': '5432'
}


def run_ohlc_query(interval, symbol):
    today = datetime.now().strftime('%Y-%m-%d')
    sql_file_path = f'queries/{interval}_query.sql'
    
    with open(sql_file_path, 'r') as file:
        query = file.read()

    query = query.replace('{{DATE}}', today).replace('{{SYMBOL}}', symbol)

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Executed {interval} OHLC for {symbol}")

def schedule_ohlc(interval):
    for symbol in SYMBOLS:
        run_ohlc_query(interval, symbol)

scheduler = BlockingScheduler()

scheduler.add_job(lambda: schedule_ohlc('15min'), 'cron', minute='*/15')
scheduler.add_job(lambda: schedule_ohlc('30min'), 'cron', minute='0,30')
scheduler.add_job(lambda: schedule_ohlc('1h'), 'cron', minute=0)
scheduler.add_job(lambda: schedule_ohlc('1d'), 'cron', hour=16, minute=0)
scheduler.add_job(lambda: schedule_ohlc('1w'), 'cron', day_of_week='fri', hour=16, minute=0)

scheduler.start()
