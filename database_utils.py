import sqlite3
import math
from datetime import datetime, timedelta

def create_connection(db_file): #make connection to the database and return con object or none.
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Exception as e:
        print(e)
    return con

def fetch_all_transactions():
    conn = create_connection("databases/transactions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    row = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return row
    
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
    
def fetch_blocks_on_main():
    conn = create_connection("databases/blocks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM blocks")
    row = cursor.fetchone()
    return int(row[0])

def chart_daily_blocks(num_days):
    con = create_connection("databases/blocks.db")
    counts_per_day = {}
    for i in range(num_days):
        date_to_fetch = datetime.now() - timedelta(days=i)
        date_str = date_to_fetch.strftime('%Y-%m-%d')
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*), DATE(timestamp) FROM blocks WHERE DATE(timestamp) = ? GROUP BY DATE(timestamp)", (date_str,))
        result = cursor.fetchone()
        if result:
            counts_per_day[date_str] = result[0]
        else:
            counts_per_day[date_str] = 0
        cursor.close() 
    con.close()
    counts_per_day = dict(reversed(list(counts_per_day.items()))) # Need to reverse, otherwise graphs are on a wrong order
    return counts_per_day

def fetch_all_node_info():
    conn = create_connection("databases/cellframe.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cellframe_data;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if rows:
        return rows
    
def fetch_top_wallets(token, amount):
    conn = create_connection("databases/wallets.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT wallet_address, token_ticker, balance FROM wallets WHERE token_ticker = '{token}' ORDER BY CAST(balance AS NUMERIC) DESC LIMIT {amount}")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if rows:
        return rows
    else:
        return None
    
def fetch_all_activated_wallets():
    conn = create_connection("databases/wallets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT wallet_address FROM wallets")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if rows:
        return len(rows)
    else:
        return None
    
def fetch_all_active_nodes():
    conn = create_connection("databases/cellframe.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM all_node_names")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if rows:
        return(len(rows))
    else:
        return None
        
def fetch_node_info_by_addr(addr):
    conn = create_connection("databases/cellframe.db")
    cursor = conn.cursor()
    addr_change = addr.replace("::","")
    addr_change = f"N{addr_change}"
    
    cursor.execute(f"SELECT all_time_signatures FROM {addr_change} ORDER BY all_time_signatures DESC LIMIT 1;")
    total_blocks_row = cursor.fetchone()
    
    cursor.execute(f"SELECT * FROM {addr_change} ORDER BY all_time_signatures DESC LIMIT 1;")
    latest_block_info = cursor.fetchone()
    
    cursor.execute(f"SELECT all_time_rewards FROM {addr_change} ORDER BY ID desc LIMIT 1;")
    all_time_rewards = cursor.fetchone()
    
    cursor.execute(f"SELECT node_version FROM {addr_change} ORDER BY ID asc LIMIT 1;")
    node_version = cursor.fetchone()
    
    cursor.execute(f"SELECT alias FROM {addr_change} ORDER BY ID asc LIMIT 1;")
    alias = cursor.fetchone()
    
    cursor.execute(f"SELECT stake_value FROM {addr_change} ORDER BY ID desc LIMIT 1;")
    stake_value = cursor.fetchone()

    results = {
        "address": addr,
        "total_blocks": total_blocks_row[0] if total_blocks_row else "N/A",
        "latest_block_info": latest_block_info,
        "all_time_rewards": all_time_rewards[0] if all_time_rewards else "N/A",
        "node_version": node_version[0],
        "alias": alias[0] if alias[0] else "N/A",
        "stake_value": stake_value[0]
    }
    
    return results