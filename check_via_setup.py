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

print("--- Via directories in config ---")
print(run_cmd("find /home/lyslama/minecraft/config -maxdepth 2 -iname '*via*'"))

print("\n--- ViaVersion log lines during boot ---")
print(run_cmd("grep -i 'via' /home/lyslama/minecraft/logs/latest.log"))

print("\n--- Geyser config remote section ---")
print(run_cmd("grep -A 10 'remote:' /home/lyslama/minecraft/config/Geyser-Fabric/config.yml"))

client.close()
