import time
import node_utils as nu
import sqlite3
import re
from datetime import datetime
import threading

def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Exception as e:
        print(e)
    return con

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
    conn = create_connection(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}_temp
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    conn.commit()
    conn.close()

def insert_data(db_name, hash, timestamp=False):
    conn = create_connection(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f"INSERT INTO {db_name}_temp (hash, timestamp) VALUES (?, ?)", (hash, timestamp))
    conn.commit()
    conn.close()

def data_exists(db_name, hash):
    conn = create_connection(f"databases/{db_name}.db")
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
    else:
        print("Failed to update blocks database!")

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
    else:
        print("Failed to update transactions database!")

def copy_to_main_table(db_name):
    conn = create_connection(f"databases/{db_name}.db")
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
    try:
        fetch_and_insert_blocks()
    except Exception as e:
        print(f"An error occurred while updating blocks: {e}")
        return
    
@every_1_minute
def update_transactions():
    print("Updating transactions database...")
    create_tables("transactions")
    try:
        fetch_and_insert_transactions()
    except Exception as e:
        print(f"An error occurred while updating transactions: {e}")
        return

@every_1_minute
def fetch_all_wallets_info():
    print("Updating wallets database...")
    conn = create_connection("databases/wallets.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS wallets (
                    wallet_address TEXT PRIMARY KEY,
                    token_ticker TEXT,
                    balance TEXT
                )''')
    conn.commit()
    list_all_wallets = nu.sendCommand("ledger list balance -net Backbone")
    pattern = re.compile(r"Ledger balance key: (\w+).+token_ticker:(\w+).+balance:(\d+)")
    matches = pattern.findall(list_all_wallets)
    if matches:
        for match in matches:
            wallet_address = match[0]
            token_ticker = match[1]
            amount = match[2]
            if wallet_address == "null":
                continue
            cursor.execute("INSERT OR IGNORE INTO wallets (wallet_address, token_ticker, balance) VALUES (?, ?, ?)", (wallet_address, token_ticker, amount))
        conn.commit()
        conn.close()
        print("Update process for wallets done!")
    else:
        return None

if __name__ == "__main__":
    tx_thread = threading.Thread(target=update_transactions)
    blocks_thread = threading.Thread(target=update_blocks)
    wallets_thread = threading.Thread(target=fetch_all_wallets_info)
    
    tx_thread.start()
    blocks_thread.start()
    wallets_thread.start()
    
    tx_thread.join()
    blocks_thread.join()
    wallets_thread.join()
