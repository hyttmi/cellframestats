import sqlite3

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