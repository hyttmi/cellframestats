import subprocess
from datetime import datetime
import re
import time
import multiprocessing as mp

def timer(fn):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = fn(*args, **kwargs)
        end_time = time.perf_counter()
        duration = (end_time - start_time)
        print(f"  Took {duration:0.4f} s")
        return result
    return wrapper

def sendCommand(command):
    full_command = f"/opt/cellframe-node/bin/cellframe-node-cli {command}"
    try:
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, full_command, output=output, stderr=error)
        
        result = output.decode('utf-8', errors='ignore').strip()
        return result
    except Exception as e:
        print(f"Exception occurred while executing command: {e}")
        return False
    
def fetch_all_blocks_hash_and_timestamp():
    cmd_output = sendCommand("block list -net Backbone -chain main")
    blocks = []
    pattern = re.findall(r"(0x[A-Z0-9]{64}): ts_create=(.*)", cmd_output)
    if pattern:
        for hashes, timestamp in pattern:
            original_datetime = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %z")
            iso8601_timestamp = original_datetime.isoformat()
            blocks.append({"hash": hashes, "timestamp": iso8601_timestamp})
        return blocks
    else:
        return None
    
def fetch_all_transactions_hash_and_timestamp():
    cmd_output = sendCommand("ledger tx -all -net Backbone")
    transactions = []
    pattern = re.findall(r"\s+Datum_tx_hash: (0x.{64})\s+TS_Created: (.*)", cmd_output)
    if pattern:
        for hashes, timestamp in pattern:
            original_datetime = datetime.strptime(timestamp, "%a %b %d %H:%M:%S %Y")
            iso8601_timestamp = original_datetime.isoformat()
            transactions.append({"hash": hashes, "timestamp": iso8601_timestamp})
        return transactions
    else:
        return None
    
def fetch_cf20_wallets_and_tokens():
    list_all_wallets = sendCommand("ledger list balance -net Backbone")
    matches = re.findall(r"\s+Ledger balance key:\s+(\w+).*\s+token_ticker: (\w+)\s+balance: (\d+)", list_all_wallets)
    wallets = []
    if matches:
        
        for match in matches:
            wallet_address = match[0]
            token_ticker = match[1]
            amount = match[2]
            wallets.append({"wallet_address": wallet_address, "token_ticker": token_ticker, "amount": amount})
        return wallets
    
    else:
        return None

@timer
def fetch_all_stake_locks():
    all_tx_output = sendCommand("ledger tx -all -net Backbone")
    if all_tx_output:
        hashes = re.findall(r"Datum_tx_hash: (0x[0-9a-fA-F]+)", all_tx_output) # Search all hashes
        released = re.findall(r"tx_prev_hash: (0x[0-9a-fA-F]+)", all_tx_output) # Search all (apparently) returned hashes
        stake_released = []
        stake_locks = []
        
        if released:
            for stakes in released:
                stake_released.append(stakes)
                
        if hashes:
            with mp.Pool() as pool: # Send all hashes to pool to check if they are srv_stake locks
                results_stake_locks = pool.map(fetch_stake_lock_by_hash, hashes)
            for result_stake_lock in results_stake_locks:
                if result_stake_lock:
                    stake_locks.append(result_stake_lock)
        
        stake_locks_set = set(stake_locks)
        stake_released_set = set(stake_released)
        stake_locks_set -= stake_released_set
        with mp.Pool() as pool:
                result_current_stake_locks = pool.map(current_stake_locks, list(stake_locks_set))
                if result_current_stake_locks:
                    print(result_current_stake_locks)

def current_stake_locks(hash):
    stakes = {}
    cmd_output = sendCommand(f"ledger tx -tx {hash} -net Backbone")
    matches = re.findall(r"TS_Created: ([^\n]+).*?type: TX_ITEM_TYPE_OUT_COND\s+data:\s+value: (\d+.\d+)\s+srv_uid: (\d+)\s+reinvest_percent: (\d+)\s+time_unlock: (\d+).*Sender addr: ([^\n]+)", cmd_output, re.DOTALL)
    if matches:
        for match in matches:
            tx_hash = hash
            ts_created = datetime.strptime(match[0], "%a %b %d %H:%M:%S %Y").isoformat()
            value = float(match[1])
            srv_uid = match[2]
            reinvest_percent = int(match[3]) / 10**18
            time_unlock = datetime.utcfromtimestamp(int(match[4])).isoformat()
            sender_addr = match[5]
            stake_info = {
                "timestamp": ts_created,
                "value": value,
                "srv_uid": srv_uid,
                "reinvest_percent": reinvest_percent,
                "time_unlock": time_unlock,
                "sender_addr": sender_addr
            }
            stakes[tx_hash] = stake_info
        return stakes

def fetch_stake_lock_by_hash(hash):
    tx_output = sendCommand(f"ledger tx -tx {hash} -net Backbone")
    if tx_output:
        srv_stake_lock = re.search(r"subtype: DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK", tx_output)
        if srv_stake_lock:
            return hash
    return None

fetch_all_stake_locks()