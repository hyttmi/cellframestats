import subprocess
import re
from datetime import datetime
import sqlite3
import multiprocessing

def sendCommand(command):
    full_command = f"/opt/cellframe-node/bin/cellframe-node-cli {command}"
    try:
        result = subprocess.check_output(full_command, shell=True, text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    
def fetch_active_nodes():
    cmd = sendCommand("srv_stake list keys -net Backbone")
    pattern = re.findall(r"Pkey hash: (0x[A-Z0-9]{64})", cmd)
    if pattern:
        return len(pattern)
    return None

def fetch_blocks_on_main():
    cmd = sendCommand("block list -net Backbone -chain main")
    pattern = re.search(r".*Have (\d+) blocks", cmd)
    if pattern:
        num_blocks = pattern.group(1)
        return int(num_blocks)
    else:
        return None
    
def fetch_all_activated_wallets():
    cmd_output = sendCommand("ledger list balance -net Backbone")
    pattern = re.findall(r"Ledger balance key: ([a-zA-Z0-9]{103}).*", cmd_output)
    if pattern:
        unique_wallets = list(set(pattern))
        return len(unique_wallets)
    else:
        return None

conn = sqlite3.connect('databases/blocks.db')
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS blocks
                 (hash TEXT PRIMARY KEY, timestamp TEXT)''')

def insert_block(hash, timestamp):
    c.execute("INSERT INTO blocks (hash, timestamp) VALUES (?, ?)", (hash, timestamp))
    conn.commit()

def block_exists(hash):
    c.execute("SELECT 1 FROM blocks WHERE hash=?", (hash,))
    return c.fetchone() is not None

def fetch_all_blocks():
    cmd_output = sendCommand("block list -net Backbone -chain main")
    blocks = []
    pattern = re.findall(r"(0x[A-Z0-9]{64}): ts_create=(.*)", cmd_output)
    if pattern:
        for hashes, timestamp in pattern:
            original_datetime = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z")
            iso8601 = original_datetime.isoformat()
            if not block_exists(hashes):
                insert_block(hashes, iso8601)
                blocks.append({"hash": hashes, "timestamp": iso8601})
    return blocks

create_table()
blocks_data = multiprocessing.Process(target=fetch_all_blocks())
blocks_data.start()
