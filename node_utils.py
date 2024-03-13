import subprocess
import re

import subprocess

import subprocess

def sendCommand(command):
    full_command = f"/opt/cellframe-node/bin/cellframe-node-cli {command}"
    try:
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, full_command, output=output, stderr=error)
        
        # Attempt to decode the output, ignoring decoding errors
        result = output.decode('utf-8', errors='ignore').strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command '{full_command}' failed with return code {e.returncode}")
        print("Standard output:")
        print(e.output)
        print("Standard error:")
        print(e.stderr)
        return f"Error: Command '{full_command}' failed with return code {e.returncode}"
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