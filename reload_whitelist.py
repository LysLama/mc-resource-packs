import socket
import paramiko
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(('192.168.2.16', 22))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.2.16', username='lyslama', password='LysLama@2112', sock=sock)

client.exec_command("tmux send-keys -t mc 'whitelist reload' C-m")
time.sleep(1)
client.exec_command("tmux send-keys -t mc 'whitelist list' C-m")
time.sleep(1)

_, stdout, _ = client.exec_command("tmux capture-pane -pt mc -S -10")
print(stdout.read().decode())

client.close()
