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

print("1. Downloading ViaFabric...")
run_cmd(client, "curl -sSL -o /home/lyslama/minecraft/mods/ViaFabric-0.4.22+185-26.x.jar https://cdn.modrinth.com/data/YlKdE5VK/versions/ki97gFLP/ViaFabric-0.4.22%2B185-26.x.jar")

out, _ = run_cmd(client, "ls -lh /home/lyslama/minecraft/mods | grep -iE 'via'")
print("All Via jars:\n", out)

print("\n2. Stopping server if needed...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh stop")
time.sleep(3)

print("3. Starting server...")
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
        print("Crash or incompatibility in console:")
        print(out)
        break
    print(f"Waiting for boot... ({(i+1)*3}s)")

print("\n4. Checking Via & Geyser in latest log:")
out, _ = run_cmd(client, "grep -iE 'viafabric|viaversion|viabackwards|geyser' /home/lyslama/minecraft/logs/latest.log | tail -n 25")
print(out)

client.close()
