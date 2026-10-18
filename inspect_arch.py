import socket
import paramiko

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

print("--- Arch / OS details ---")
out, _ = run_cmd(client, "cat /etc/os-release | grep -E 'NAME|ID'")
print(out)

print("\n--- Minecraft logs / version ---")
out, _ = run_cmd(client, "grep -m 1 'Loading Minecraft' /home/lyslama/minecraft/logs/latest.log")
print(out)
out, _ = run_cmd(client, "grep -m 1 'Loading Fabric Loader' /home/lyslama/minecraft/logs/latest.log")
print(out)

print("\n--- Minecraft server status ---")
out, _ = run_cmd(client, "tmux capture-pane -pt mc -S -10 2>/dev/null")
print(out)

print("\n--- Mods list ---")
out, _ = run_cmd(client, "ls -1 /home/lyslama/minecraft/mods")
print(out)

print("\n--- Check playit / pacman ---")
out, _ = run_cmd(client, "which playit 2>/dev/null || echo 'playit not found'")
print(out)
out, _ = run_cmd(client, "which yay 2>/dev/null || which paru 2>/dev/null || which pacman 2>/dev/null")
print(out)

client.close()
