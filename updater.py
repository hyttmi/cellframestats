import time
import node_utils as nu
import sqlite3
import re
from datetime import datetime
import threading

def every_5_minutes(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            time.sleep(5 * 60)
    return wrapper

def every_1_minute(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            time.sleep(60)
    return wrapper

def create_tables(db_name):
    conn = sqlite3.connect(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}_temp
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    conn.commit()
    conn.close()

def insert_data(db_name, hash, timestamp):
    conn = sqlite3.connect(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f"INSERT INTO {db_name}_temp (hash, timestamp) VALUES (?, ?)", (hash, timestamp))
    conn.commit()
    conn.close()

def data_exists(db_name, hash):
    conn = sqlite3.connect(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f"SELECT 1 FROM {db_name} WHERE hash=?", (hash,))
    result = c.fetchone() is not None
    conn.close()
    return result

def fetch_and_insert_blocks():
    cmd_output = nu.sendCommand("block list -net Backbone -chain main")
    blocks = []
    pattern = re.findall(r"(0x[A-Z0-9]{64}): ts_create=(.*)", cmd_output)
    if pattern:
        for hashes, timestamp in pattern:
            original_datetime = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z")
            iso8601 = original_datetime.isoformat()
            if not data_exists("blocks", hashes):
                insert_data("blocks", hashes, iso8601)
                blocks.append({"hash": hashes, "timestamp": iso8601})
    copy_to_main_table("blocks")

def fetch_and_insert_transactions():
    cmd_output = nu.sendCommand("ledger tx -all -net Backbone")
    transactions = []
    pattern = re.findall(r"transaction:.*hash (0x[A-Z0-9].*)\s+TS Created: (.*)", cmd_output)
    if pattern:
        for hashes, timestamp in pattern:
            original_datetime = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %Y")
            iso8601 = original_datetime.isoformat()
            if not data_exists("transactions", hashes):
                insert_data("transactions", hashes, iso8601)
                transactions.append({"hash": hashes, "timestamp": iso8601})
    copy_to_main_table("transactions")

def copy_to_main_table(db_name):
    conn = sqlite3.connect(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f"DELETE FROM {db_name}")
    c.execute(f"INSERT INTO {db_name} SELECT * FROM {db_name}_temp")
    conn.commit()
    print(f"Update process for {db_name} done!")
    conn.close()

@every_5_minutes
def update_blocks():
    print("Updating blocks database...")
    create_tables("blocks")
    fetch_and_insert_blocks()
    
@every_1_minute
def update_transactions():
    print("Updating transactions database...")
    create_tables("transactions")
    fetch_and_insert_transactions()

if __name__ == "__main__":
    tx_thread = threading.Thread(target=update_transactions)
    blocks_thread = threading.Thread(target=update_blocks)
    
    tx_thread.start()
    blocks_thread.start()
    
    tx_thread.join()
    blocks_thread.join()
