import socket
import paramiko
import zipfile
import io

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.connect(('192.168.2.16', 22))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.2.16', username='lyslama', password='LysLama@2112', sock=sock)

sftp = client.open_sftp()
with sftp.open('/home/lyslama/minecraft/mods/hardcorerevival-fabric-26.3-26.3.0.1.jar', 'rb') as f:
    jar_bytes = f.read()
sftp.close()
client.close()

z = zipfile.ZipFile(io.BytesIO(jar_bytes))
data = z.read('net/blay09/mods/hardcorerevival/handler/KnockoutHandler.class')

# Let's inspect references in KnockoutHandler
import re
print("Method calls / signatures in KnockoutHandler:")
for s in re.findall(b'([a-zA-Z0-9_/$]+;?\(.*?\)[a-zA-Z0-9_/$]+;?)', data):
    print(" ", s.decode('ascii', errors='ignore'))

