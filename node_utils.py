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
    pattern = re.compile(r"(0x[A-Z0-9]{64}): ts_create=(.*)")
    match = pattern.findall(cmd_output)
    if match:
        for hashes, timestamp in match:
            blocks.append({"hash": hashes, "timestamp": u.convert_timestamp_to_iso8601(timestamp)})
        return blocks
    else:
        return None

def fetch_all_transactions_hash_and_timestamp():
    cmd_output = sendCommand("ledger tx -all -net Backbone")
    if cmd_output:
        transactions = []
        pattern = re.compile(r"\s+Datum_tx_hash: (0x.{64})\s+TS_Created: (.*)")
        match = pattern.findall(cmd_output)
        if match:
            for hashes, timestamp in match:
                transactions.append({"hash": hashes, "timestamp": u.convert_timestamp_to_iso8601(timestamp)})
            print(transactions)
            return transactions
        else:
            return None
    else:
        return None

def fetch_cf20_wallets_and_tokens():
    list_all_wallets = sendCommand("ledger list balance -net Backbone")
    pattern = re.compile(r"\s+Ledger balance key:\s+(Rj.{102}).*\s+token_ticker: (\w+)\s+balance: (\d+)")
    matches = pattern.findall(list_all_wallets)
    wallets = []
    if matches:
        for match in matches:
            wallet_address = match[0]
            token_ticker = match[1]
            amount = match[2]
            if wallet_address != "null":
                wallets.append({"wallet_address": wallet_address, "token_ticker": token_ticker, "amount": amount})
        print(wallets)
        return wallets 
    else:
        return None

@u.timer    
def fetch_all_stake_locks():
    all_tx_output = sendCommand("ledger tx -all -net Backbone")
    stake_lock_info = []
    if all_tx_output:
        pattern = re.compile(r"Datum_tx_hash: (0x[0-9a-fA-F]+)") # Search all hashes
        hashes = pattern.findall(all_tx_output)
        if hashes:
            with mp.Pool() as pool:
                result_current_locks = pool.map(info_stake_locks, hashes)
                for result in result_current_locks:
                    if result is not None and "OUT - : 0" not in result[7]:
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
    pattern = re.compile(r"TS_Created: ([^\n]+)"
                     r".*?Token_ticker: CELL"
                     r".*?type: TX_ITEM_TYPE_OUT_COND\s+data:\s+value: (\d+\.\d+)\s+srv_uid: (\d+)\s+reinvest_percent: (\d+)\s+time_unlock: (\d+)"
                     r".*?Sender addr: ([^\n]+)"
                     r".*?Spent OUTs:(.*)", re.DOTALL)
    match_stake_lock = pattern.search(cmd_output)

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