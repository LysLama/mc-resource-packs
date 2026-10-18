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

# 1. Update Geyser config
print("1. Updating Geyser config to auth-type: floodgate and passthrough-motd...")
cfg_path = '/home/lyslama/minecraft/config/Geyser-Fabric/config.yml'
out, _ = run_cmd(client, f"sed -i 's/auth-type: online/auth-type: floodgate/g' {cfg_path}")
out, _ = run_cmd(client, f"sed -i 's/passthrough-motd: false/passthrough-motd: true/g' {cfg_path}")
out, _ = run_cmd(client, f"sed -i 's/passthrough-server-name: false/passthrough-server-name: true/g' {cfg_path}")

out, _ = run_cmd(client, f"grep -E 'auth-type|passthrough' {cfg_path}")
print("Updated config values:\n", out)

# 2. Reload Geyser via tmux
print("\n2. Reloading Geyser in Minecraft console...")
run_cmd(client, "tmux send-keys -t mc 'geyser reload' C-m")
time.sleep(3)
out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -15")
print(out)

# 3. Check playit commands
print("\n3. Testing playit binary...")
out, err = run_cmd(client, "/home/lyslama/playit --help")
print("Playit help:\n", out[:500] if out else err)

client.close()
