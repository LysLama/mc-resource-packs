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

# Let's inspect HardcoreRevivalConfig
cfg_class = z.read('net/blay09/mods/hardcorerevival/config/HardcoreRevivalConfig.class')
import re
print("Config fields:")
for m in re.findall(b'Lnet/blay09/mods/balm/api/config/BalmConfigData;.*?([a-zA-Z0-9]+)', cfg_class):
    print(" ", m.decode('ascii', errors='ignore'))

# Or print all string constants in config
print("\nAll strings in HardcoreRevivalConfig:")
for s in re.findall(b'[\x20-\x7e]{4,}', cfg_class):
    print(" ", s.decode('ascii', errors='ignore'))
