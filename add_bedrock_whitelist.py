import socket
import paramiko
import json
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(('192.168.2.16', 22))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.2.16', username='lyslama', password='LysLama@2112', sock=sock)

def run_cmd(cmd):
    _, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='replace').strip()

# 1. Read whitelist.json
sftp = client.open_sftp()
with sftp.open('/home/lyslama/minecraft/whitelist.json', 'r') as f:
    whitelist = json.loads(f.read().decode('utf-8'))

# Check if .LysLama is already in whitelist
bedrock_entry = {
    "uuid": "00000000-0000-0000-0009-01f5ba08ca69",
    "name": ".LysLama"
}

exists = any(item.get('name') == '.LysLama' or item.get('uuid') == bedrock_entry['uuid'] for item in whitelist)
if not exists:
    whitelist.append(bedrock_entry)
    print("Added .LysLama to whitelist.json list.")
else:
    print(".LysLama already in list.")

with sftp.open('/home/lyslama/minecraft/whitelist.json', 'w') as f:
    f.write(json.dumps(whitelist, indent=2))
sftp.close()

print("2. Reloading whitelist on Minecraft server...")
run_cmd("tmux send-keys -t mc 'whitelist reload' C-m")
time.sleep(1)
run_cmd("tmux send-keys -t mc 'whitelist list' C-m")
time.sleep(1)

out = run_cmd("tmux capture-pane -pt mc -S -10")
print("Console output:\n", out)

client.close()
