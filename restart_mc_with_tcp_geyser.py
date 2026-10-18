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

print("1. Checking use-direct-connection in config...")
out, _ = run_cmd(client, f"grep -n 'use-direct-connection' {cfg}")
print("Config line:", out)

print("\n2. Stopping Minecraft server completely...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh stop")
time.sleep(3)

for i in range(20):
    out, _ = run_cmd(client, "tmux has-session -t mc 2>/dev/null && echo RUNNING || echo STOPPED")
    if out == "STOPPED":
        print("Server stopped cleanly.")
        break
    time.sleep(1)

print("\n3. Starting Minecraft server with new config...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh start")

ready = False
for i in range(30):
    time.sleep(3)
    out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -30 2>/dev/null")
    if "Done (" in out:
        ready = True
        print(f"Server is READY in {(i+1)*3}s!")
        break
    if "Incompatible mods found" in out or "Crash report" in out:
        print("Crash or error found in console:")
        print(out)
        break
    print(f"Waiting for boot... ({(i+1)*3}s)")

print("\n4. Checking latest Geyser logs:")
out, _ = run_cmd(client, "grep -iE 'geyser|floodgate' /home/lyslama/minecraft/logs/latest.log | tail -n 25")
print(out)

client.close()
