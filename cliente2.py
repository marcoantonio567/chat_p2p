import socket
import sys
import threading
import time
import random

class Server:
    connections = []
    peers = []

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', 10000))
        sock.listen(1)

        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.start()  # Corrigido para iniciar o thread
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]), 'conectado')
            self.sendPeers()

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            for connection in self.connections:
                connection.send(data)

            if not data:
                print(str(a[0]) + ':' + str(a[1]), 'desconectado')
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, "utf-8"))

class Cliente:
    def sendMSG(self, sock):
        while True:
            sock.send(bytes(input(""), 'utf-8'))

    def __init__(self, peer):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer, 10000))

        iThread = threading.Thread(target=self.sendMSG, args=(sock,))
        iThread.daemon = True
        iThread.start()

        while True:
            data = sock.recv(1024)
            if not data:
                break
            if not data[0:1] == b'\x11':
                self.updatePeers(data[1:])
            else:
                print(str(data, 'utf-8'))

    def updatePeers(self, peersData):
        Server.peers = str(peersData, "utf-8").split(",")[:-1]

class P2P:
    peers = ['127.0.0.1']

while True:
    try:
        print("tentando conectar ")
        time.sleep(random.randint(1, 5))
        for peer in P2P.peers:
            try:
                cliente = Cliente(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                if random.randint(1, 20) == 1:
                    try:
                        server = Server()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    except:
                        print("não foi possível iniciar o servidor")
    except KeyboardInterrupt:
        sys.exit(0)
