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

print("Stopping server cleanly...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh stop")

for i in range(20):
    out, _ = run_cmd(client, "tmux has-session -t mc 2>/dev/null && echo RUNNING || echo STOPPED")
    if out == "STOPPED":
        print("Server stopped cleanly.")
        break
    time.sleep(1)

print("Starting server with Geyser & Floodgate...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh start")

ready = False
for i in range(30):
    time.sleep(3)
    out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -30 2>/dev/null")
    if "Done (" in out:
        ready = True
        print(f"Server is READY in {(i+1)*3}s!")
        break
    if "Crash report" in out or "Encountered an unexpected exception" in out:
        print("CRASH DETECTED:")
        print(out)
        break
    print(f"Waiting for boot... ({(i+1)*3}s)")

print("\n--- Recent console logs (Geyser / Floodgate) ---")
out, _ = run_cmd(client, "grep -iE 'geyser|floodgate' /home/lyslama/minecraft/logs/latest.log | tail -n 25")
print(out)

print("\n--- Check UDP 19132 listening status ---")
out, _ = run_cmd(client, "ss -u -a -n -p | grep 19132 || echo 'Port 19132 not found'")
print(out)

client.close()
