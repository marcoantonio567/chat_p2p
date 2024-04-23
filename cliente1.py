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
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]), 'conectado')
            self.sendPeers()

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            if data:
                for connection in self.connections:
                    connection.send(data)

                print(str(a[0]) + ':' + str(a[1]), 'enviou:', str(data, 'utf-8'))
            else:
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
            connection.send(bytes(p, "utf-8"))

class Cliente:
    def __init__(self, peer):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((peer, 10000))

        self.name = input("Digite seu nome: ")  # Solicita ao usuário que insira seu nome

        iThread = threading.Thread(target=self.sendMSG)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            else:
                print(self.name, 'recebeu:', str(data, 'utf-8'))

    def sendMSG(self):
        while True:
            msg = input("Digite uma mensagem: ")
            self.sock.send(bytes(self.name + ": " + msg, 'utf-8'))  # Adiciona o nome à mensagem antes de enviar

class P2P:
    peers = ['127.0.0.1']

while True:
    try:
        print("Tentando conectar...")
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
                        print("Não foi possível iniciar o servidor")
    except KeyboardInterrupt:
        sys.exit(0)
