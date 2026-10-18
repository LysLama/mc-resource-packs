import socket
import paramiko

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(('192.168.2.16', 22))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.2.16', username='lyslama', password='LysLama@2112', sock=sock)

def run_cmd(cmd):
    _, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("--- force-resource-packs setting ---")
print(run_cmd("grep -n -C 3 'force-resource-packs' /home/lyslama/minecraft/config/Geyser-Fabric/config.yml"))

print("\n--- packs directory ---")
print(run_cmd("ls -la /home/lyslama/minecraft/config/Geyser-Fabric/packs"))

client.close()
