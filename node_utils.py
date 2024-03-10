import subprocess
import re

def sendCommand(command):
    full_command = f"/opt/cellframe-node/bin/cellframe-node-cli {command}"
    try:
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, full_command, output=output, stderr=error)
        result = output.strip()
        return result
    except Exception as e:
        print(f"Exception occurred while executing command: {e}")
        return f"Error: {e}"
    
def fetch_active_nodes():
    cmd = sendCommand("srv_stake list keys -net Backbone")
    pattern = re.findall(r"Pkey hash: (0x[A-Z0-9]{64})", cmd)
    if pattern:
        return len(pattern)
    return None
    
def fetch_all_activated_wallets():
    cmd_output = sendCommand("ledger list balance -net Backbone")
    pattern = re.findall(r"Ledger balance key: ([a-zA-Z0-9]{103}).*", cmd_output)
    if pattern:
        unique_wallets = list(set(pattern))
        return len(unique_wallets)
    else:
        return None
    
def fetch_all_wallets_info():
    list_all_wallets = sendCommand("ledger list balance -net Backbone")
    pattern = re.compile(r"Ledger balance key: (\w+).+token_ticker:(\w+).+balance:(\d+)")
    matches = pattern.findall(list_all_wallets)
    if matches:
        wallet_totals = {}
        for match in matches:
            wallet_address = match[0]
            token_ticker = match[1]
            amount = int(match[2])
            if wallet_address == "null":
                continue
            if token_ticker not in ["mCELL", "CELL"]:
                continue
            if wallet_address not in wallet_totals:
                wallet_totals[wallet_address] = {}
            wallet_totals[wallet_address][token_ticker] = wallet_totals[wallet_address].get(token_ticker, 0) + amount
        result = [
            {
                "Wallet address": wallet_address,
                "Balances": [
                    {"Token": token, "Amount": amount}
                    for token, amount in wallet_totals[wallet_address].items()
                ]
            }
            for wallet_address in wallet_totals
        ]
        return result
    else:
        return None

def fetch_top_wallets(token, amount):
    all_wallets_info = fetch_all_wallets_info()
    
    wallets = [
        {"Wallet address": wallet["Wallet address"], f"{token} balance": sum(balance["Amount"] for balance in wallet["Balances"] if balance["Token"] == f"{token}")}
        for wallet in all_wallets_info
    ]
    
    sorted_wallets = sorted(wallets, key=lambda x: x[f"{token} balance"], reverse=True)
    
    return sorted_wallets[:amount]