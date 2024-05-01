import node_utils as nu
import database_utils as du
import utils as u

from datetime import datetime
import threading
import requests
import time

def create_tables(db_name):
    conn = du.create_connection(f"databases/{db_name}.db")
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}_temp
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 hash TEXT,
                 timestamp TEXT)''')
    c.execute(f'''CREATE TABLE IF NOT EXISTS {db_name}
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 hash TEXT,
                 timestamp TEXT)''')
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

def update_blocks():
    print("Updating blocks database...")
    create_tables("blocks")
    try:
        insert_blocks_to_database()
    except Exception as e:
        print(f"An error occurred while updating blocks: {e}")
        return
    
def update_transactions():
    print("Updating transactions database...")
    create_tables("transactions")
    try:
        insert_transactions_to_database()
    except Exception as e:
        print(f"An error occurred while updating transactions: {e}")
        return

def update_cf20_wallets_info():
    wallets = nu.fetch_cf20_wallets_and_tokens()
    print("Updating wallets database...")
    if wallets is not None:
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
        for wallet in wallets:
            wallet_address = wallet["wallet_address"]
            token_ticker = wallet["token_ticker"]
            amount = wallet["amount"]
            cursor.execute("INSERT INTO cf20_temp (wallet_address, token_ticker, balance) VALUES (?, ?, ?)", (wallet_address, token_ticker, amount))
        conn.commit()
        cursor.execute("DROP TABLE IF EXISTS cf20")
        cursor.execute("ALTER TABLE cf20_temp RENAME TO cf20")
        print("Update process for wallets done!")
    else:
        print("No wallets found.")
    conn.close()
    
def update_stakes_info():
    print("Updating stakes database...")
    data = nu.fetch_all_stake_locks()
    if data is not None:
        conn = du.create_connection("databases/stakes.db")
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS stakes
                          (tx_hash TEXT PRIMARY KEY, 
                          ts_created TEXT, 
                          value REAL, 
                          srv_uid TEXT, 
                          reinvest_percent REAL, 
                          time_unlock TEXT, 
                          sender_addr TEXT)''')

        cursor.executemany('''INSERT OR IGNORE INTO stakes
                                      (tx_hash, ts_created, value, srv_uid, reinvest_percent, time_unlock, sender_addr) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        conn.close()
        print("Update process for stakes done!")
    else:
        print("Stakes not updated as there was no new data to process!") # There's no data if there's no new stakes.

def update_cf20_wallets_daily():
    wallets = nu.fetch_cf20_wallets_and_tokens()
    print("Updating wallets daily amount...")
    if wallets is not None:
        conn = du.create_connection("databases/wallets.db")
        cursor = conn.cursor()
        for wallet in wallets:
            wallet_address = wallet["wallet_address"]
            token_ticker = wallet["token_ticker"]
            amount = wallet["amount"]
            cursor.execute(f'''CREATE TABLE IF NOT EXISTS {wallet_address} (
                                    date TEXT,
                                    token_ticker TEXT,
                                    amount REAL
                                )''')
            cursor.execute(f"DELETE FROM {wallet_address} WHERE date <= date('now', '-365 day')") # 365 days of data is enough I guess...
            cursor.execute(f"INSERT OR REPLACE INTO {wallet_address} (date, token_ticker, amount) VALUES (?, ?, ?)",(datetime.now().strftime("%Y-%m-%d"), token_ticker, amount))
        conn.commit()
        print("Update process for wallets done!")
    else:
        print("No wallets found.")
    conn.close()

def fetch_latest_database_from_cellframestats(filename):
    print("Updating cellframe.db...")
    url = f"http://cellframestats.com/{filename}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(f"databases/{filename}", "wb") as file:
            file.write(response.content)
        print(f"{filename} updated succesfully!")
    else:
        print(f"Failed to download {filename}!")
        
def execute_thread(thread):
    try:
        thread.start()
        thread.join()
        time.sleep(30)
    except:
        pass

if __name__ == "__main__":
    try:
        running = True
        while running:
            blocks_thread = threading.Thread(target=update_blocks)
            transactions_thread = threading.Thread(target=update_transactions)
            wallets_thread = threading.Thread(target=update_cf20_wallets_info)
            stakes_thread = threading.Thread(target=update_stakes_info)
            cellframedb_thread = threading.Thread(target=fetch_latest_database_from_cellframestats, args=("cellframe.db",))
            wallets_daily_thread = threading.Thread(target=update_cf20_wallets_daily)

            execute_thread(blocks_thread)
            execute_thread(transactions_thread)
            execute_thread(wallets_thread)
            execute_thread(stakes_thread)
            execute_thread(cellframedb_thread)
            execute_thread(wallets_daily_thread)

    except KeyboardInterrupt:
        print("Exiting...")
        running = False