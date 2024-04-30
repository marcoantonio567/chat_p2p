import socket
import threading
import sys

class Server:
    def __init__(self):
        self.connections = []
        self.peers = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)
        print("Servidor rodando ...")

        self.promptThread = threading.Thread(target=self.promptMsg)
        self.promptThread.daemon = True
        self.promptThread.start()

        while True:
            c, a = self.sock.accept()
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]), "conectado")
            threading.Thread(target=self.clientHandler, args=(c, a)).start()

    def clientHandler(self, c, a):
        while True:
            try:
                data = c.recv(1024)
                if not data:
                    print(str(a[0]) + ':' + str(a[1]), "desconectado")
                    self.connections.remove(c)
                    self.peers.remove(a[0])
                    c.close()
                    self.sendPeers()
                    break
                else:
                    msg = data.decode('utf-8')
                    print(f"{a[0]} diz: {msg}")
                    self.broadcast(msg, c)
            except:
                break

    def broadcast(self, msg, sender):
        for connection in self.connections:
            if connection != sender:
                try:
                    connection.send(bytes(msg, 'utf-8'))
                except:
                    continue

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + "," 

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, 'utf-8'))

    def promptMsg(self):
        while True:
            try:
                msg = input("")
                self.broadcast("[Servidor] " + msg, None)
            except KeyboardInterrupt:
                sys.exit(0)

class Client:
    def __init__(self, address):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((address, 10000))

        threading.Thread(target=self.receiveMsg).start()
        self.sendMsg()

    def receiveMsg(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if data:
                    print(data.decode('utf-8'))
                else:
                    break
            except:
                break

    def sendMsg(self):
        while True:
            try:
                msg = input("")
                self.sock.send(bytes(msg, 'utf-8'))
            except:
                break

class p2p:
    peers = ['127.0.0.1']

while True:
    try:
        print("Tentando conectar ...")
        for peer in p2p.peers:
            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass

        try:
            server = Server()
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("Não foi possível iniciar o servidor ...")

    except KeyboardInterrupt:
        sys.exit(0)
