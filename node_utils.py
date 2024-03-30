import subprocess
from datetime import datetime
import re
import multiprocessing as mp
import utils as u

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
    matches = re.findall(r"\s+Ledger balance key:\s+(Rj.{102}).*\s+token_ticker: (\w+)\s+balance: (\d+)", list_all_wallets)
    wallets = []
    if matches:
        for match in matches:
            wallet_address = match[0]
            token_ticker = match[1]
            amount = match[2]
            if wallet_address != "null":
                wallets.append({"wallet_address": wallet_address, "token_ticker": token_ticker, "amount": amount})
        return wallets
    
    else:
        return None
    
def fetch_all_stake_locks():
    all_tx_output = sendCommand("ledger tx -all -net Backbone")
    stake_lock_info = []
    if all_tx_output:
        hashes = re.findall(r"Datum_tx_hash: (0x[0-9a-fA-F]+)", all_tx_output) # Search all hashes
        if hashes:
            with mp.Pool() as pool:
                result_current_locks = pool.map(info_stake_locks, hashes)
                for result in result_current_locks:
                    if result is not None:
                        if "OUT - : 0" in result[7]:
                            continue
                        tx_hash = result[0]
                        ts_created = result[1]
                        value = result[2]
                        srv_uid = result[3]
                        reinvest_percent = result[4]
                        time_unlock = result[5]
                        sender_addr = result[6]
                        stake_lock_info.append((tx_hash, ts_created, value, srv_uid, reinvest_percent, time_unlock, sender_addr))
    return stake_lock_info

def info_stake_locks(hash):
    cmd_output = sendCommand(f"ledger tx -tx {hash} -net Backbone")
    match_stake_lock = re.search(r"TS_Created: ([^\n]+).*?Token_ticker: CELL.*?type: TX_ITEM_TYPE_OUT_COND\s+data:\s+value: (\d+\.\d+)\s+srv_uid: (\d+)\s+reinvest_percent: (\d+)\s+time_unlock: (\d+).*?Sender addr: ([^\n]+).*?Spent OUTs:(.*)", cmd_output, re.DOTALL)

    if match_stake_lock:
        ts_created = datetime.strptime(match_stake_lock.group(1), "%a %b %d %H:%M:%S %Y").isoformat()
        value = float(match_stake_lock.group(2))
        srv_uid = match_stake_lock.group(3)
        reinvest_percent = int(match_stake_lock.group(4)) / 10**18
        time_unlock = datetime.utcfromtimestamp(int(match_stake_lock.group(5))).isoformat()
        sender_addr = match_stake_lock.group(6)
        rest_data = match_stake_lock.group(7)
        
        stake_info = (
            hash,
            ts_created,
            value,
            srv_uid,
            reinvest_percent,
            time_unlock,
            sender_addr,
            rest_data
        )
        return stake_info
    else: # It's not a stake transaction
        return None