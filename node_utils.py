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
