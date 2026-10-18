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

print("1. Downloading Floodgate-Fabric...")
out, err = run_cmd(client, "curl -sSL -o /home/lyslama/minecraft/mods/Floodgate-Fabric-2.2.7-b69.jar https://cdn.modrinth.com/data/bWrNNfkb/versions/m9eO07Zi/Floodgate-Fabric-2.2.7-b69.jar")
if err: print("Err:", err)

print("2. Downloading Geyser-Fabric...")
out, err = run_cmd(client, "curl -sSL -o /home/lyslama/minecraft/mods/Geyser-Fabric-2.11.3-b1247.jar https://cdn.modrinth.com/data/wKkoqHrH/versions/zwyI6L8t/Geyser-Fabric-2.11.3-b1247.jar")
if err: print("Err:", err)

print("\n3. Verifying mod jars...")
out, _ = run_cmd(client, "ls -lh /home/lyslama/minecraft/mods | grep -iE 'geyser|floodgate'")
print(out)

client.close()
