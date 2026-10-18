import socket
import paramiko
import os
import time

LOCAL_PACK = r'D:\Download\actions-stuff-v-1-11-1.mcpack'
REMOTE_PACK_DIR = '/home/lyslama/minecraft/config/Geyser-Fabric/packs'
REMOTE_PACK_FILE = f'{REMOTE_PACK_DIR}/actions-stuff-v-1-11-1.mcpack'

print(f"1. Checking local file: {LOCAL_PACK} ({os.path.getsize(LOCAL_PACK):,} bytes)...")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(('192.168.2.16', 22))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.2.16', username='lyslama', password='LysLama@2112', sock=sock)

def run_cmd(cmd):
    _, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("2. Uploading pack to Geyser packs folder via SFTP...")
sftp = client.open_sftp()
sftp.put(LOCAL_PACK, REMOTE_PACK_FILE)
sftp.close()
print("Upload complete!")

print("3. Verifying remote file...")
print(run_cmd(f"ls -lh {REMOTE_PACK_DIR}"))

print("4. Reloading Geyser configurations...")
run_cmd("tmux send-keys -t mc 'geyser reload' C-m")
time.sleep(3)

print("5. Checking console logs for pack loading...")
out = run_cmd("tmux capture-pane -pt mc -S -20")
print(out)

client.close()
