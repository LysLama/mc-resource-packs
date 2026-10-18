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
    # Extract readable strings of length >= 4
    strings = re.findall(b'[\x20-\x7e]{4,}', data)
    for s in strings:
        decoded = s.decode('ascii', errors='ignore')
        if any(keyword in decoded for keyword in [
            'pose', 'Pose', 'entity', 'Entity', 'packet', 'Packet', 'rescue', 'Rescue',
            'knock', 'Knock', 'reviv', 'Reviv', 'sync', 'Sync', 'move', 'Move', 'interact',
            'sneak', 'Sneak', 'death', 'Death', 'health', 'Health', 'effect', 'Effect',
            'custom', 'Custom', 'message', 'Message', 'send', 'Send'
        ]):
            print(" ", decoded)

inspect_class('net/blay09/mods/hardcorerevival/handler/KnockoutHandler.class')
inspect_class('net/blay09/mods/hardcorerevival/handler/KnockoutRestrictionHandler.class')
inspect_class('net/blay09/mods/hardcorerevival/handler/RescueHandler.class')
inspect_class('net/blay09/mods/hardcorerevival/handler/KnockoutSyncHandler.class')
inspect_class('net/blay09/mods/hardcorerevival/mixin/ServerPlayerMixin.class')
