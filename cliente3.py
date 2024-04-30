import socket
import sys
import threading
import time
import random

class Server:
    connections = []  # Lista para rastrear todas as conexões
    peers = []        # Lista para rastrear os endereços IP dos peers conectados

    def __init__(self):
        # Cria um socket TCP/IP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilização do endereço
        sock.bind(('localhost', 10000))  # Liga o socket ao endereço localhost na porta 10000
        sock.listen(15)  # Habilita o socket para aceitar conexões, com um limite de 15 conexões pendentes

        while True:
            c, a = sock.accept()  # Aceita uma conexão do cliente
            cThread = threading.Thread(target=self.handler, args=(c, a))  # Cria uma nova thread para lidar com a conexão
            cThread.start()  # Inicia a thread
            self.connections.append(c)  # Adiciona a nova conexão à lista de conexões
            self.peers.append(a[0])  # Adiciona o endereço IP do cliente à lista de peers
            print(str(a[0]) + ':' + str(a[1]), 'conectado')  # Exibe o endereço IP e porta do cliente conectado
            self.sendPeers()  # Envia a lista de peers para todos os clientes conectados

    def handler(self, c, a):
        while True:
            data = c.recv(1024)  # Recebe dados do cliente
            if data:
                for connection in self.connections:
                    connection.send(data)  # Encaminha os dados recebidos para todos os outros clientes

                print(str(a[0]) + ':' + str(a[1]), 'enviou:', str(data, 'utf-8'))  # Exibe os dados enviados pelo cliente
            else:
                print(str(a[0]) + ':' + str(a[1]), 'desconectado')  # Exibe quando um cliente se desconecta
                self.connections.remove(c)  # Remove a conexão da lista de conexões
                self.peers.remove(a[0])  # Remove o endereço IP do cliente da lista de peers
                c.close()  # Fecha a conexão com o cliente
                self.sendPeers()  # Envia a lista atualizada de peers para os clientes restantes
                break

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","  # Constrói uma string contendo os endereços IP dos peers

        for connection in self.connections:
            connection.send(bytes(p, "utf-8"))  # Envia a string de endereços IP para todos os clientes conectados

class Cliente:
    def __init__(self, peer):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((peer, 10000))  # Conecta-se ao peer especificado na porta 10000

        self.name = input("Digite seu nome: ")  # Solicita ao usuário que insira seu nome

        iThread = threading.Thread(target=self.sendMSG)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)  # Recebe dados do servidor
            if not data:
                break
            else:
                print(self.name, 'recebeu:', str(data, 'utf-8'))  # Exibe os dados recebidos

    def sendMSG(self):
        while True:
            msg = input("Digite uma mensagem: ")
            self.sock.send(bytes(self.name + ": " + msg, 'utf-8'))  # Envia a mensagem para o servidor

class P2P:
    peers = ['127.0.0.1']  # Define uma lista de peers iniciais (apenas o localhost)

while True:
    try:
        print("Tentando conectar...")
        time.sleep(random.randint(1, 5))  # Aguarda um tempo aleatório antes de tentar se conectar
        for peer in P2P.peers:
            try:
                cliente = Cliente(peer)  # Tenta conectar-se a cada peer na lista
            except KeyboardInterrupt:  # Captura a exceção de interrupção do teclado (geralmente Ctrl+C)
                sys.exit(0)  # Sai do programa
            except:
                if random.randint(1, 20) == 1:  # Se ocorrer uma exceção com probabilidade de 1/20
                    try:
                        server = Server()  # Tenta iniciar um servidor
                    except KeyboardInterrupt:
                        sys.exit(0)  # Sai do programa
                    except:
                        print("Não foi possível iniciar o servidor")  # Exibe uma mensagem se não for possível iniciar o servidor
    except KeyboardInterrupt:
        sys.exit(0)  # Sai do programa se uma interrupção do teclado for detectada
