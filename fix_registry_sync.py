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

# 1. Update viafabric.yml
via_cfg = '/home/lyslama/minecraft/config/ViaFabric/viafabric.yml'
print("1. Updating viafabric.yml ignore-registry-sync-errors to true...")
run_cmd(client, f"sed -i 's/ignore-registry-sync-errors: false/ignore-registry-sync-errors: true/g' {via_cfg}")
out, _ = run_cmd(client, f"grep 'ignore-registry-sync-errors' {via_cfg}")
print("Config:", out)

# 2. Download modernregsyncfix-2.0.0.jar
print("\n2. Downloading modernregsyncfix-2.0.0.jar...")
run_cmd(client, "curl -sSL -o /home/lyslama/minecraft/mods/modernregsyncfix-2.0.0.jar https://cdn.modrinth.com/data/U2w9BZus/versions/LmIVtB3w/modernregsyncfix-2.0.0.jar")
out, _ = run_cmd(client, "ls -lh /home/lyslama/minecraft/mods/modernregsyncfix-2.0.0.jar")
print("Downloaded:", out)

# 3. Stop server cleanly
print("\n3. Stopping server cleanly...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh stop")
time.sleep(3)

for i in range(20):
    out, _ = run_cmd(client, "tmux has-session -t mc 2>/dev/null && echo RUNNING || echo STOPPED")
    if out == "STOPPED":
        print("Server stopped.")
        break
    time.sleep(1)

# 4. Start server
print("\n4. Starting server with registry bypass...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh start")

ready = False
for i in range(35):
    time.sleep(3)
    out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -30 2>/dev/null")
    if "Done (" in out:
        ready = True
        print(f"Server is READY in {(i+1)*3}s!")
        break
    if "Crash report" in out or "Incompatible mods found" in out:
        print("Crash or error found in console:")
        print(out)
        break
    print(f"Waiting for boot... ({(i+1)*3}s)")

# 5. Wait for Geyser UDP 19132
print("\n5. Waiting for Geyser UDP 19132...")
for i in range(10):
    out, _ = run_cmd(client, "ss -u -l -n -p | grep 19132")
    if out:
        print("Geyser port 19132 is open!")
        break
    time.sleep(2)

client.close()
