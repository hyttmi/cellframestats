import time
import node_utils as nu
import sqlite3
import re
from datetime import datetime

def create_table():
    conn = sqlite3.connect('databases/blocks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS blocks_temp
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')
    conn.commit()
    conn.close()

def insert_block(hash, timestamp):
    conn = sqlite3.connect('databases/blocks.db')
    c = conn.cursor()
    c.execute("INSERT INTO blocks_temp (hash, timestamp) VALUES (?, ?)", (hash, timestamp))
    conn.commit()
    conn.close()

def block_exists(hash):
    conn = sqlite3.connect('databases/blocks.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM blocks WHERE hash=?", (hash,))
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
            if not block_exists(hashes):
                insert_block(hashes, iso8601)
                blocks.append({"hash": hashes, "timestamp": iso8601})
    copy_to_main_table()

def copy_to_main_table():
    conn = sqlite3.connect('databases/blocks.db')
    c = conn.cursor()
    c.execute('DELETE FROM blocks')
    c.execute('INSERT INTO blocks SELECT * FROM blocks_temp')
    conn.commit()
    print("Update process done!")
    conn.close()

def update_blocks():
    create_table()
    while True:
        fetch_and_insert_blocks()
        print("Running updater...")
        time.sleep(300)

if __name__ == "__main__":
    update_blocks()
