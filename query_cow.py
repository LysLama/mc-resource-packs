import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.2.16', username='lyslama', password='LysLama@2112')
# Wake up server and query a cow
ssh.exec_command('tmux send-keys -t mc "execute as @e[type=cow,limit=1] run data get entity @s" Enter')
time.sleep(1)
stdin, stdout, stderr = ssh.exec_command('tmux capture-pane -pt mc -S -30')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
