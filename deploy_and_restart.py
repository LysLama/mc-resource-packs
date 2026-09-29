import paramiko
import time
import re

REMOTE_HOST = '192.168.2.16'
USERNAME = 'lyslama'
PASSWORD = 'LysLama@2112'
PROPERTIES_PATH = '/home/lyslama/minecraft/server.properties'
NEW_SHA1 = '8c2d573d50b6102d7349b9cd76fc5aee32fa9383'

def run_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return exit_status, out, err

def main():
    print(f"Connecting to {REMOTE_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(REMOTE_HOST, username=USERNAME, password=PASSWORD, timeout=10)

    try:
        # 1. Update server.properties
        print("Reading server.properties...")
        sftp = ssh.open_sftp()
        with sftp.open(PROPERTIES_PATH, 'r') as f:
            content = f.read().decode('utf-8')

        # Replace resource-pack-sha1
        new_content = re.sub(r'resource-pack-sha1=.*', f'resource-pack-sha1={NEW_SHA1}', content)
        with sftp.open(PROPERTIES_PATH, 'w') as f:
            f.write(new_content)
        sftp.close()
        print(f"Updated server.properties with sha1={NEW_SHA1}")

        # Verify
        status, out, err = run_cmd(ssh, f"grep resource-pack-sha1 {PROPERTIES_PATH}")
        print(f"Verified remote: {out.strip()}")

        # 2. Check current players before restart
        status, out, err = run_cmd(ssh, "tmux capture-pane -pt mc -S -20 2>/dev/null")
        print("Recent console tail:")
        print(out[-300:] if out else "tmux session not running or empty")

        # 3. Stop server cleanly
        print("\nStopping server cleanly via mc.sh stop...")
        run_cmd(ssh, "/home/lyslama/minecraft/mc.sh stop")

        # Wait for tmux session mc to exit
        stopped = False
        for _ in range(30):
            status, out, err = run_cmd(ssh, "tmux has-session -t mc 2>/dev/null")
            if status != 0:
                stopped = True
                print("Server tmux session closed successfully.")
                break
            time.sleep(2)
        
        if not stopped:
            print("Warning: server didn't stop in 60s, checking processes...")
            run_cmd(ssh, "pkill -f 'fabric-server-mc'")
            time.sleep(3)

        # 4. Start server
        print("\nStarting server via mc.sh start...")
        run_cmd(ssh, "/home/lyslama/minecraft/mc.sh start")

        # 5. Monitor startup log
        print("Waiting for server to complete startup...")
        started = False
        start_time = time.time()
        while time.time() - start_time < 90:
            status, out, err = run_cmd(ssh, "tail -n 25 /home/lyslama/minecraft/logs/latest.log 2>/dev/null")
            if "Done (" in out:
                started = True
                print(">>> SERVER STARTED SUCCESSFULLY! <<<")
                for line in out.splitlines():
                    if "Done (" in line:
                        print("Startup info:", line)
                break
            time.sleep(3)

        if not started:
            print("Server took longer than 90s, current log:")
            print(out[-500:])

    finally:
        ssh.close()
        print("SSH connection closed.")

if __name__ == '__main__':
    main()
