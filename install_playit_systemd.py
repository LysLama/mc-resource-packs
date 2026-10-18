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

# 1. Kill tmux session playit
run_cmd(client, "tmux kill-session -t playit 2>/dev/null")

# 2. Write systemd unit file
service_text = """[Unit]
Description=Playit.gg Tunnel Daemon
After=network.target

[Service]
Type=simple
User=lyslama
WorkingDirectory=/home/lyslama
ExecStart=/home/lyslama/playit --socket-path /tmp/playit.sock --secret-path /home/lyslama/.config/playit/playit.toml -l /home/lyslama/playit.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

sftp = client.open_sftp()
with sftp.open('/home/lyslama/playit.service', 'w') as f:
    f.write(service_text)
sftp.close()

out, err = run_cmd(client, "echo 'LysLama@2112' | sudo -S mv /home/lyslama/playit.service /etc/systemd/system/playit.service")
out, err = run_cmd(client, "echo 'LysLama@2112' | sudo -S systemctl daemon-reload")
out, err = run_cmd(client, "echo 'LysLama@2112' | sudo -S systemctl enable --now playit")

time.sleep(2)
out, err = run_cmd(client, "systemctl status playit --no-pager")
print("Systemd Service Status:\n", out)

client.close()
