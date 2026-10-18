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

print("--- 1. Search LysLama in logs ---")
out, _ = run_cmd(client, "grep -i 'lyslama' /home/lyslama/minecraft/logs/latest.log | tail -n 20")
print(out)

print("\n--- 2. Current whitelist.json ---")
out, _ = run_cmd(client, "cat /home/lyslama/minecraft/whitelist.json 2>/dev/null")
print(out)

print("\n--- 3. Running whitelist commands ---")
# Vanilla whitelist add
run_cmd(client, "tmux send-keys -t mc 'whitelist add .LysLama' C-m")
time.sleep(1)
# Floodgate whitelist add (fwhitelist is specifically designed for Bedrock players without dot)
run_cmd(client, "tmux send-keys -t mc 'fwhitelist add LysLama' C-m")
time.sleep(1)
# Reload whitelist
run_cmd(client, "tmux send-keys -t mc 'whitelist reload' C-m")
time.sleep(1)

out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -15")
print("Console output:\n", out)

print("\n--- 4. Updated whitelist.json ---")
out, _ = run_cmd(client, "cat /home/lyslama/minecraft/whitelist.json 2>/dev/null")
print(out)

client.close()
