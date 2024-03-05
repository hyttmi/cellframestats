import subprocess
import re

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
    
def fetch_all_activated_wallets():
    cmd_output = sendCommand("ledger list balance -net Backbone")
    pattern = re.findall(r"Ledger balance key: ([a-zA-Z0-9]{103}).*", cmd_output)
    if pattern:
        unique_wallets = list(set(pattern))
        return len(unique_wallets)
    else:
        return None
        
        