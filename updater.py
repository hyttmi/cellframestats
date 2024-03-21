import time
import node_utils as nu
import database_utils as du
import sqlite3
import re
from datetime import datetime
import threading

def every_new_day(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                current_time = datetime.datetime.now().time()
                if current_time.hour == 0 and current_time.minute == 0:
                    func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            time.sleep(60)
    return wrapper

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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 hash TEXT,
                 timestamp DATE)''')
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 hash TEXT,
                 timestamp DATE)''')
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

def insert_blocks_to_database():
    blocks = nu.fetch_all_blocks_hash_and_timestamp()
    if blocks is not None:
        for block in blocks:
            hashes = block["hash"]
            timestamp = block["timestamp"]
            if not data_exists("blocks", hashes):
                insert_data("blocks", hashes, timestamp)
        copy_to_main_table("blocks")
    else:
        print("Failed to update blocks database!")

def insert_transactions_to_database():
    transactions = nu.fetch_all_transactions_hash_and_timestamp()
    if transactions is not None:
        for transaction in transactions:
            hashes = transaction["hash"]
            timestamp = transaction["timestamp"]
            if not data_exists("transactions", hashes):
                insert_data("transactions", hashes, timestamp)
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
        insert_blocks_to_database()
    except Exception as e:
        print(f"An error occurred while updating blocks: {e}")
        return
    
@every_1_minute
def update_transactions():
    print("Updating transactions database...")
    create_tables("transactions")
    try:
        insert_transactions_to_database()
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