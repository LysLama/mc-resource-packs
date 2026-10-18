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

print("--- Check Geyser Config ---")
out, _ = run_cmd(client, "grep -E 'auth-type|port:|address:|clone-remote-port' /home/lyslama/minecraft/config/Geyser-Fabric/config.yml")
print(out)

print("\n--- Download Playit CLI ---")
out, err = run_cmd(client, "curl -sSL -o /home/lyslama/playit https://github.com/playit-cloud/playit-agent/releases/download/v1.0.10/playit-linux-amd64 && chmod +x /home/lyslama/playit")
print("Downloaded playit:", out, err)

out, _ = run_cmd(client, "ls -lh /home/lyslama/playit")
print(out)

out, _ = run_cmd(client, "/home/lyslama/playit --version")
print("Playit version:", out)

client.close()
