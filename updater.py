import time
import node_utils as nu
import database_utils as du
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
    conn = du.create_connection(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}_temp
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    conn.commit()
    conn.close()

def insert_data(db_name, hash, timestamp=False):
    conn = du.create_connection(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f"INSERT INTO {db_name}_temp (hash, timestamp) VALUES (?, ?)", (hash, timestamp))
    conn.commit()
    conn.close()

def data_exists(db_name, hash):
    conn = du.create_connection(f"databases/{db_name}.db")
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
    pattern = re.findall(r"\s+Datum_tx_hash: (0x.{64})\s+TS_Created: (.*)", cmd_output)
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
    conn = du.create_connection(f"databases/{db_name}.db")
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

@every_5_minutes
def fetch_cf20_wallets_info():
    print("Updating wallets database...")
    conn = du.create_connection("databases/wallets.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cf20 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet_address TEXT,
                    token_ticker TEXT,
                    balance REAL
                )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cf20_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallet_address TEXT,
                    token_ticker TEXT,
                    balance REAL
                )''')    
    conn.commit()
    
    list_all_wallets = nu.sendCommand("ledger list balance -net Backbone")
    pattern = re.compile(r"\s+Ledger balance key:\s+(\w+).*\s+token_ticker: (\w+)\s+balance: (\d+)")
    matches = pattern.findall(list_all_wallets)
    
    if matches:
        for match in matches:
            wallet_address = match[0]
            token_ticker = match[1]
            amount = match[2]
            if wallet_address == "null":
                continue
            cursor.execute("INSERT INTO cf20_temp (wallet_address, token_ticker, balance) VALUES (?, ?, ?)", (wallet_address, token_ticker, amount))
            
        conn.commit()
        
        cursor.execute("DROP TABLE IF EXISTS cf20")
        cursor.execute("ALTER TABLE cf20_temp RENAME TO cf20")
        print("Update process for wallets done!")
    else:
        print("No wallets found.")
    
    conn.close()

if __name__ == "__main__":
    tx_thread = threading.Thread(target=update_transactions)
    blocks_thread = threading.Thread(target=update_blocks)
    wallets_thread = threading.Thread(target=fetch_cf20_wallets_info)
    
    tx_thread.start()
    blocks_thread.start()
    wallets_thread.start()
    
    tx_thread.join()
    blocks_thread.join()
    wallets_thread.join()