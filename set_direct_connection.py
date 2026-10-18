import socket
import paramiko
import time

def get_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(('192.168.2.16', 22))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.2.16', username='lyslama', password='LysLama@2112', sock=sock)
    return client

def run_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

client = get_client()

cfg = '/home/lyslama/minecraft/config/Geyser-Fabric/config.yml'

print("1. Updating use-direct-connection to false...")
run_cmd(client, f"sed -i 's/use-direct-connection: true/use-direct-connection: false/g' {cfg}")

out, _ = run_cmd(client, f"grep 'use-direct-connection' {cfg}")
print("Config:", out)

print("\n2. Reloading Geyser...")
run_cmd(client, "tmux send-keys -t mc 'geyser reload' C-m")
time.sleep(3)

out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -20")
print("Console:\n", out)

client.close()
