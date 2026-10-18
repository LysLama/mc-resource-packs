import socket
import paramiko
import time
import re

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

print("1. Preparing playit directory...")
run_cmd(client, "mkdir -p /home/lyslama/.config/playit")

# Kill any existing playit session
run_cmd(client, "tmux kill-session -t playit 2>/dev/null")

print("2. Starting playit in tmux session 'playit'...")
run_cmd(client, 'tmux new-session -d -s playit "cd /home/lyslama && /home/lyslama/playit --secret-path /home/lyslama/.config/playit/playit.toml 2>&1"')

time.sleep(3)

print("3. Capturing playit console output...")
out, _ = run_cmd(client, "tmux capture-pane -pt playit -S -50")
print(out)

# Check for claim URL
urls = re.findall(r'https://playit\.gg/claim/\S+', out)
if urls:
    print(f"\nFOUND CLAIM URL: {urls[0]}")
else:
    print("\nNo claim URL pattern matched, full output above.")

client.close()
