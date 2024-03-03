import sqlite3
import math
from datetime import datetime, timedelta

def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Exception as e:
        print(e)
    return con

def fetch_all_transactions():
    conn = create_connection("databases/cellframe.db")
    cursor = conn.cursor()

    cursor.execute("SELECT cumulative_transactions FROM transactions ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return int(row[0])
    else:
        return None
    
def fetch_all_staked_tokens():
    conn = create_connection("databases/cellframe.db")
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM stakes;")
    row = cursor.fetchall()
    cursor.close()
    conn.close()
    if row:
        values = []
        for amount in row:
            values.append(float(amount[0]))
        return round(math.fsum(values))    
def chart_daily_blocks(num_days):
    con = create_connection("databases/blocks.db")
    counts_per_day = {}
    for i in range(num_days):
        date_to_fetch = datetime.now() - timedelta(days=i)
        date_str = date_to_fetch.strftime('%Y-%m-%d')
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*), DATE(timestamp) FROM blocks WHERE DATE(timestamp) = ? GROUP BY DATE(timestamp)", (date_str,))
        result = cursor.fetchone()
        if result:
            counts_per_day[date_str] = result[0]
        else:
            counts_per_day[date_str] = 0
        cursor.close()  # Close the cursor to release resources
    con.close()  # Close the connection
    return counts_per_day
