import paramiko
import time
import os
import socket
import struct
import json

REMOTE_HOST = '192.168.2.16'
USERNAME = 'lyslama'
PASSWORD = 'LysLama@2112'
LOCAL_ICON = r'C:\Users\thanh\.gemini\antigravity\scratch\mc-resource-packs\icon_option_1.png'
REMOTE_ICON = '/home/lyslama/minecraft/server-icon.png'

def run_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return exit_status, out, err

def pack_varint(val):
    total = b''
    while True:
        byte = val & 0x7F
        val >>= 7
        if val != 0:
            byte |= 0x80
        total += bytes([byte])
        if val == 0:
            break
    return total

def read_varint(sock):
    val = 0
    shift = 0
    while True:
        b = sock.recv(1)
        if not b:
            raise EOFError("Socket closed")
        byte = b[0]
        val |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return val

def ping_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((REMOTE_HOST, 25565))
    
    # Handshake packet: packet ID 0x00, protocol version 767 (1.21), host, port 25565, next state 1 (status)
    host_bytes = REMOTE_HOST.encode('utf-8')
    handshake = (
        pack_varint(0x00) +
        pack_varint(767) +
        pack_varint(len(host_bytes)) + host_bytes +
        struct.pack('>H', 25565) +
        pack_varint(1)
    )
    sock.sendall(pack_varint(len(handshake)) + handshake)
    
    # Status request: packet ID 0x00
    request = pack_varint(0x00)
    sock.sendall(pack_varint(len(request)) + request)
    
    # Read response
    _ = read_varint(sock)  # Packet length
    packet_id = read_varint(sock)
    length = read_varint(sock)  # String length
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    sock.close()
    return json.loads(data.decode('utf-8'))

def main():
    print(f"Connecting to {REMOTE_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(REMOTE_HOST, username=USERNAME, password=PASSWORD, timeout=10)

    try:
        # 1. Upload icon_option_1.png to /home/lyslama/minecraft/server-icon.png
        print(f"Uploading {LOCAL_ICON} -> {REMOTE_ICON}...")
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_ICON, REMOTE_ICON)
        sftp.close()
        print("Upload successful!")

        # Verify file size on remote
        status, out, err = run_cmd(ssh, f"ls -l {REMOTE_ICON}")
        print(f"Remote file: {out.strip()}")

        # 2. Stop server cleanly
        print("\nStopping Minecraft server via mc.sh stop...")
        run_cmd(ssh, "/home/lyslama/minecraft/mc.sh stop")

        stopped = False
        for _ in range(30):
            status, out, err = run_cmd(ssh, "tmux has-session -t mc 2>/dev/null")
            if status != 0:
                stopped = True
                print("Server stopped cleanly.")
                break
            time.sleep(2)

        if not stopped:
            print("Warning: server didn't stop in 60s, checking tmux pane...")
            status, out, err = run_cmd(ssh, "tmux capture-pane -pt mc -S -20 2>/dev/null")
            print(out)

        # 3. Start server
        print("\nStarting Minecraft server via mc.sh start...")
        run_cmd(ssh, "/home/lyslama/minecraft/mc.sh start")

        # 4. Wait for server to be ready
        print("Waiting for server startup...")
        ready = False
        for i in range(40):
            time.sleep(3)
            status, out, err = run_cmd(ssh, "tmux capture-pane -pt mc -S -30 2>/dev/null")
            if 'Done (' in out:
                ready = True
                print("Server is fully started!")
                for line in out.splitlines():
                    if 'Done (' in line:
                        print(f"  -> {line.strip()}")
                break
            print(f"Waiting... ({i*3}s)")

        if not ready:
            print("Warning: Server took longer than expected to show 'Done'.")

        # 5. SLP ping test
        print("\nPerforming SLP ping to verify server-icon...")
        try:
            res = ping_server()
            print("Ping response received!")
            print(f"MOTD: {res.get('description')}")
            favicon = res.get('favicon')
            if favicon:
                print(f"Favicon present: True (Length: {len(favicon)} chars, starts with {favicon[:40]}...)")
            else:
                print("Favicon NOT found in ping response!")
        except Exception as e:
            print(f"SLP ping failed: {e}")

    finally:
        ssh.close()

if __name__ == '__main__':
    main()
