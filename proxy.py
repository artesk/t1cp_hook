#!/usr/bin/python
import socket
import select
import time
import sys
import re

buffer_size = 4096
delay = 0.0001
# Адрес и порт хранилища
forward_to = ('localhost', 1542)

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except (Exception,e):
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print ("Ошибка установки соединения, закрытие соединения", clientaddr)
            clientsock.close()

    def on_close(self):
        print(self.s.getpeername(), "has disconnected")
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        self.channel[out].close()
        self.channel[self.s].close()
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        strrecieve = str(data)
        if strrecieve.find("DevDepot_commitObjects")>0:
            base = re.findall(re.compile('alias=\"(.+?)\"'),strrecieve)
            # Здесь действие хука
            print(base)
        self.channel[self.s].send(data)

if __name__ == '__main__':
    # порт, которые слушаем
        server = TheServer('', 1313)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print ("Ctrl C - Stopping server")
            sys.exit(1)