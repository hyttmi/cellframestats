import subprocess
from datetime import datetime
import re

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
        return f"Error: {e}"
    
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

def fetch_all_stake_locks():
    cmd_output = sendCommand("ledger tx -all -net Backbone")
    if cmd_output:

        locked = re.compile(r"Datum_tx_hash: (0x[0-9a-fA-F]+)(?:(?!Datum_tx_hash:).)*subtype: DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_LOCK", re.DOTALL)
        released = re.compile(r"tx_prev_hash: (0x[0-9a-fA-F]+)")

        locked_stakes = []
        released_stakes = []

        matches_locked = locked.findall(cmd_output)
        if matches_locked:
            for match in matches_locked:
                locked_stakes.append(match)

        matches_released = released.findall(cmd_output)
        if matches_released:
            for match in matches_released:
                released_stakes.append(match)

        locked_stakes_set = set(locked_stakes)
        released_stakes_set = set(released_stakes)

        locked_stakes_set -= released_stakes_set

        locked_stakes_set = list(locked_stakes_set)

        return locked_stakes_set
    else:
        return None

def current_stake_locks():
    stake_locks = fetch_all_stake_locks()
    stakes = {}
    for hash in stake_locks:
        cmd_output = sendCommand(f"ledger tx -tx {hash} -net Backbone")
        matches = re.findall(r"Datum_tx_hash: (0x[0-9a-fA-F]+)\s+TS_Created: ([^\n]+).*?type: TX_ITEM_TYPE_OUT_COND\s+data:\s+value: (\d+.\d+)\s+srv_uid: (\d+)\s+reinvest_percent: (\d+)\s+time_unlock: (\d+)", cmd_output, re.DOTALL)
        for match in matches:
            tx_hash = match[0]
            ts_created = datetime.strptime(match[1], "%a %b %d %H:%M:%S %Y").isoformat()
            value = float(match[2])
            srv_uid = match[3]
            reinvest_percent = int(match[4]) / 10**18
            time_unlock = datetime.utcfromtimestamp(int(match[5])).isoformat()
            stake_info = {
                "timestamp": ts_created,
                "value": value,
                "srv_uid": srv_uid,
                "reinvest_percent": reinvest_percent,
                "time_unlock": time_unlock
            }
            stakes[tx_hash] = stake_info
    return stakes