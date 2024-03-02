import sqlite3
import math

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
    
def chart_daily_blocks(amount):
    con = create_connection("databases/cellframe.db")
    with con:
        cur = con.cursor()
        query = f"""SELECT date, daily_transactions FROM transactions ORDER BY id DESC LIMIT {amount}"""
        cur.execute(query)
        results = cur.fetchall()
        reversed_results = list(reversed(results))
        return reversed_results