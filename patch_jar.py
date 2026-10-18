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

print("1. Patching jar via remote Python...")
remote_py = """
import zipfile
import json
import shutil
import os

jar_path = '/home/lyslama/minecraft/mods/Geyser-Fabric-2.11.3-b1247.jar'
tmp_jar = '/home/lyslama/minecraft/mods/Geyser-patched.jar'

with zipfile.ZipFile(jar_path, 'r') as zin:
    with zipfile.ZipFile(tmp_jar, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'fabric.mod.json':
                doc = json.loads(data.decode('utf-8'))
                print('Original depends:', doc.get('depends'))
                doc['depends']['minecraft'] = '>=26.2'
                data = json.dumps(doc).encode('utf-8')
                print('Patched depends:', doc.get('depends'))
            zout.writestr(item, data)

shutil.move(tmp_jar, jar_path)
print('Successfully replaced jar!')
"""

out, err = run_cmd(client, f"python3 -c \"{remote_py}\"")
print(out)
if err: print("Err:", err)

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
    if "Incompatible mods found" in out or "Crash report" in out or "Encountered an unexpected exception" in out:
        print("Crash or error found in console:")
        print(out)
        break
    print(f"Waiting for boot... ({(i+1)*3}s)")

print("\n4. Checking Geyser in logs:")
out, _ = run_cmd(client, "grep -iE 'geyser|floodgate' /home/lyslama/minecraft/logs/latest.log | tail -n 25")
print(out)

print("\n5. Checking UDP 19132:")
out, _ = run_cmd(client, "ss -u -a -n -p | grep 19132 || echo 'Port 19132 not open'")
print(out)

client.close()
