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

# 1. Kill any stale playit processes
print("1. Cleaning old playit...")
run_cmd(client, "pkill -9 -f playit 2>/dev/null; tmux kill-session -t playit 2>/dev/null; rm -f /tmp/playit.sock /home/lyslama/playit.log /home/lyslama/playit-setup.log")
time.sleep(1)

# 2. Start daemon in tmux
print("2. Starting playit daemon...")
run_cmd(client, "tmux new-session -d -s playit '/home/lyslama/playit --socket-path /tmp/playit.sock --secret-path /home/lyslama/.config/playit/playit.toml -l /home/lyslama/playit.log'")
time.sleep(2)

# 3. Start setup in background redirecting to log
print("3. Running playit-cli setup in background...")
run_cmd(client, "nohup /home/lyslama/playit-cli --socket-path /tmp/playit.sock setup > /home/lyslama/playit-setup.log 2>&1 &")

# 4. Poll log for URL
print("4. Waiting for Claim URL...")
for i in range(10):
    time.sleep(1)
    out, _ = run_cmd(client, "cat /home/lyslama/playit-setup.log 2>/dev/null")
    if out:
        print("Setup log output:")
        print(out)
        urls = re.findall(r'https://playit\.gg/claim/\S+', out)
        if urls:
            print("\n" + "="*50)
            print("CLAIM URL:", urls[0])
            print("="*50)
            break

client.close()
