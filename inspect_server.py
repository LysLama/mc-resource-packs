import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.2.16', username='lyslama', password='LysLama@2112', timeout=10)

def cmd(c):
    _, stdout, stderr = ssh.exec_command(c)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("--- OS info ---")
print(cmd("cat /etc/os-release"))
print("Arch:", cmd("uname -m"))

print("\n--- Minecraft logs / version ---")
print(cmd("grep -m 1 'Loading Minecraft' /home/lyslama/minecraft/logs/latest.log"))
print(cmd("grep -m 1 'Loading Fabric Loader' /home/lyslama/minecraft/logs/latest.log"))

print("\n--- Installed mods ---")
print(cmd("ls -1 /home/lyslama/minecraft/mods"))

print("\n--- Systemd / sudo check ---")
print("sudo check:", cmd("echo 'LysLama@2112' | sudo -S which systemctl 2>/dev/null"))
print("playit check:", cmd("which playit 2>/dev/null || echo 'not installed'"))

ssh.close()
