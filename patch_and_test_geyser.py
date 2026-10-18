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

print("1. Patching Geyser-Fabric fabric.mod.json...")
script = (
    "rm -rf /tmp/geyser_patch && mkdir -p /tmp/geyser_patch && cd /tmp/geyser_patch && "
    "unzip -q /home/lyslama/minecraft/mods/Geyser-Fabric-2.11.3-b1247.jar fabric.mod.json && "
    "sed -i 's/\"minecraft\":\"~26.2\"/\"minecraft\":\">=26.2\"/g' fabric.mod.json && "
    "zip -q -u /home/lyslama/minecraft/mods/Geyser-Fabric-2.11.3-b1247.jar fabric.mod.json && "
    "rm -rf /tmp/geyser_patch"
)
out, err = run_cmd(client, script)
print("Patch out:", out, "err:", err)

dep, _ = run_cmd(client, 'unzip -p /home/lyslama/minecraft/mods/Geyser-Fabric-2.11.3-b1247.jar fabric.mod.json | grep -o \'"minecraft":[^,}]*\'')
print("Patched dependency:", dep)

print("\n2. Stopping server if running...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh stop")
time.sleep(3)

print("3. Starting server...")
run_cmd(client, "/home/lyslama/minecraft/mc.sh start")

ready = False
for i in range(25):
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

print("\n4. Checking Geyser in logs:")
out, _ = run_cmd(client, "grep -iE 'geyser|floodgate' /home/lyslama/minecraft/logs/latest.log | tail -n 20")
print(out)

print("\n5. Checking UDP 19132:")
out, _ = run_cmd(client, "ss -u -a -n -p | grep 19132 || echo 'Port 19132 not open'")
print(out)

client.close()
