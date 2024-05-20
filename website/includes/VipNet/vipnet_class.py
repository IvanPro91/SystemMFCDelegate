import time
from socket import socket

import paramiko

class VipNet:
    def __init__(self, password="nhecktekjpf,", user="user"):
        self.user = user
        self.password = password
        self.host = '172.20.15.1'
        self.port = 22
        self.width = 600
        self.port = 22
        self.max_bytes = 60000

    def getTransportMFTP(self):
        client = paramiko.SSHClient()
        result = []
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=self.host,
                       username=self.user,
                       password=self.password,
                       port=self.port)
        with client.invoke_shell(width=self.width) as ssh:
            ssh.send("mftp view\n")
            ssh.settimeout(5)
            ssh.set_combine_stderr(True)
            int = 1
            while True:
                try:
                    part = ssh.recv(self.max_bytes).decode('KOI8-R')
                    if '(END)' in part:
                        ssh.send("Q\n")
                        break
                    #print(str(part).replace("--", ""))

                    time.sleep(0.3)
                    splits = str(part).replace("\r", "") \
                        .replace("\n", "") \
                        .replace("--", "") \
                        .replace("__", "") \
                        .replace("  ", " ") \
                        .replace("\x1b[K:\x1b[K", "") \
                        .replace("\x1b[K", str(int)) \
                        .split('|')
                    ssh.send("\n")
                    if splits[0] != "" and len(splits) == 11:
                        int += 1
                        for i in range(0, len(splits)):
                            splits[i] = str(splits[i]).strip()

                        if splits[2][0] == '@':
                            splits.append("Отправлено")
                        if splits[2][0] == 'K':
                            splits.append("Доставлено")
                        if splits[2][0] == 'R':
                            splits.append("Прочитано")
                        if splits[2][0] == '~':
                            splits.append("Отправлено")

                        if splits[1][0] == '@':
                            splits.append("Отправлено")
                        if splits[1][0] == 'K':
                            splits.append("Доставлено")
                        if splits[1][0] == 'R':
                            splits.append("Прочитано")
                        if splits[1][0] == '~':
                            splits.append("Отправлено")
                        result.append(splits)
                except socket.timeout:
                    return False, 'TimeOut'
            return True, result
