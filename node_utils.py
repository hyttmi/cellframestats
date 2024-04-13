import subprocess
from datetime import datetime
import re
import os
import multiprocessing as mp
import utils as u
import pytest

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
    cmd_output = sendCommand("tx_history -all -net Backbone")
    if cmd_output:
        transactions = []
        pattern = re.compile(r"status: ACCEPTED\s+hash: (0x.{64}).*?tx_created: ([^\n]+)", re.DOTALL)
        match = pattern.findall(cmd_output)
        if match:
            for hashes, timestamp in match:
                transactions.append({"hash": hashes, "timestamp": u.convert_timestamp_to_iso8601(timestamp)})
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
        return wallets 
    else:
        return None

def fetch_all_stake_locks():
    all_tx_output = sendCommand("tx_history -all -net Backbone")
    stake_lock_info = []
    if all_tx_output:
        pattern = re.compile(r"hash: (0x[0-9a-fA-F]+)", re.MULTILINE) # Search all hashes
        hashes = pattern.findall(all_tx_output)
        if hashes:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tx_hashes_file_path = os.path.join(script_dir, "tx_hashes.txt")
            existing_hashes = set()
            if os.path.exists(tx_hashes_file_path):
                with open(tx_hashes_file_path, "r") as f:
                    for line in f:
                        existing_hashes.add(line.strip())
            new_hashes = [hash for hash in hashes if hash not in existing_hashes] # Only process new hashes, saves about 35+ seconds for now...
            if new_hashes:
                with open(tx_hashes_file_path, "a") as stake_hashes_file:
                    stake_hashes_file.write("\n".join(new_hashes) + "\n")
            with mp.Pool() as pool:
                result_current_locks = pool.map(info_stake_locks, new_hashes)
                for result in result_current_locks:
                    if result is not None:
                        tx_hash = result[0]
                        ts_created = result[1]
                        value = result[2]
                        srv_uid = result[3]
                        reinvest_percent = result[4]
                        time_unlock = result[5]
                        sender_addr = result[6]
                        stake_lock_info.append((tx_hash, ts_created, value, srv_uid, reinvest_percent, time_unlock, sender_addr))
                        existing_hashes.add(tx_hash)
            return stake_lock_info
    else:
        return None

def info_stake_locks(hash):
    cmd_output = sendCommand(f"ledger info -hash {hash} -net Backbone")
    if "OUT - : 0" not in cmd_output: # Not released stakes only
        pattern = re.compile(r"TS_Created: ([^\n]+)\s+Token_ticker: CELL.*?type: TX_ITEM_TYPE_OUT_COND\s+data:\s+value: (\d+\.\d+)\s+srv_uid: (\d+)\s+reinvest_percent: (\d+)\s+time_unlock: (\d+).*?Sender addr: (Rj.{102})", re.DOTALL)
        match_stake_lock = pattern.search(cmd_output)

        if match_stake_lock:
            ts_created = datetime.strptime(match_stake_lock.group(1), "%a %b %d %H:%M:%S %Y").isoformat()
            value = float(match_stake_lock.group(2))
            srv_uid = match_stake_lock.group(3)
            reinvest_percent = int(match_stake_lock.group(4)) / 10**18
            time_unlock = datetime.utcfromtimestamp(int(match_stake_lock.group(5))).isoformat()
            sender_addr = match_stake_lock.group(6)

            stake_info = (
                hash,
                ts_created,
                value,
                srv_uid,
                reinvest_percent,
                time_unlock,
                sender_addr
            )
            return stake_info
        else: # It's not a stake transaction
            return None
    
def test_run():
    functions = [
        fetch_all_blocks_hash_and_timestamp,
        fetch_all_transactions_hash_and_timestamp,
        fetch_cf20_wallets_and_tokens,
        fetch_all_stake_locks
    ]
    for function in functions:
        result = function()
        assert result is not None, f"{function.__name__} returned None"