import socket
import paramiko
import zipfile
import io
import re

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

def inspect_class(name):
    print(f"\n================ {name} ================")
    data = z.read(name)
    strings = re.findall(b'[\x20-\x7e]{4,}', data)
    for s in strings:
        decoded = s.decode('ascii', errors='ignore')
        print(" ", decoded)

inspect_class('net/blay09/mods/hardcorerevival/mixin/ServerGamePacketListenerImplMixin.class')
inspect_class('net/blay09/mods/hardcorerevival/mixin/LivingEntityMixin.class')
inspect_class('net/blay09/mods/hardcorerevival/mixin/PlayerMixin.class')
