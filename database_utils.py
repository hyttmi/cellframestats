import sqlite3
import math

def fetch_all_transactions():
    conn = sqlite3.connect('databases/cellframe.db')
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
    conn = sqlite3.connect('databases/cellframe.db')
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