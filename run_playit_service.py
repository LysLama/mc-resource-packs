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

print("1. Cleaning previous state...")
run_cmd(client, "tmux kill-session -t playit 2>/dev/null")
run_cmd(client, "rm -f /home/lyslama/playit.log /tmp/playit.sock")
run_cmd(client, "mkdir -p /home/lyslama/.config/playit")

print("2. Launching playit in tmux...")
cmd = (
    "tmux new-session -d -s playit "
    "'/home/lyslama/playit --socket-path /tmp/playit.sock --secret-path /home/lyslama/.config/playit/playit.toml -l /home/lyslama/playit.log'"
)
out, err = run_cmd(client, cmd)
print("Launch out:", out, "err:", err)

for i in range(5):
    time.sleep(2)
    out, _ = run_cmd(client, "cat /home/lyslama/playit.log 2>/dev/null")
    if out:
        print(f"Log content (at {i*2}s):")
        print(out)
        if "https://playit.gg/claim/" in out:
            break

pane, _ = run_cmd(client, "tmux capture-pane -pt playit -S -30 2>/dev/null")
print("\nTmux pane output:")
print(pane)

urls = re.findall(r'https://playit\.gg/claim/\S+', out + "\n" + pane)
if urls:
    print(f"\n==========================================")
    print(f"CLAIM URL FOUND: {urls[0]}")
    print(f"==========================================")

client.close()
