import socket
import threading
import time

# Variáveis globais para controle
identification = input("Como você deseja ser identificado? ")
shutdown_event = threading.Event()
client_socket = None
client_sockets = []
server_host = None
server_port = None
is_promoted = False  # Variável para controlar se já houve uma promoção

# Função para receber mensagens
def receive_messages(client_socket, client_address):
    global is_promoted
    while True:
        try:
            # Recebe a mensagem do cliente
            message = client_socket.recv(1024).decode('utf-8')
            if message == "servidor_encerrado":
                print("O servidor foi desligado. Você será promovido a servidor.")
                # Verifique se já houve uma promoção
                if not is_promoted:
                    is_promoted = True
                    client_socket.close()
                    # Inicia servidor local
                    start_server('localhost', server_port)
                return
            print(message)
            # Envie a mensagem recebida para todos os outros clientes
            for client in client_sockets:
                if client != client_socket:
                    client.send(message.encode('utf-8'))
        except Exception as e:
            print("[Erro]:", e)
            break

# Função para enviar mensagens
def send_message(client_socket):
    while True:
        message = input()
        try:
            client_socket.send(f"{identification}: {message}".encode('utf-8'))
            if message.lower() == "/sair":
                client_socket.close()
                break
        except Exception as e:
            print("[Erro]:", e)
            break

# Função para desligar o servidor
def shutdown_server(server_socket):
    print("Desligando o servidor...")
    shutdown_event.set()
    
    for client_socket in client_sockets:
        try:
            client_socket.send(b"servidor_encerrado")
            client_socket.close()
        except Exception as e:
            print("[Erro ao fechar socket do cliente]:", e)
    server_socket.close()
    print("Servidor desligado com sucesso.")

# Função para iniciar o cliente
def start_client(server_ip, server_port):
    global client_socket, is_promoted
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print("Conectado ao servidor.")

        def monitor_server_connection():
            global is_promoted
            while not shutdown_event.is_set():
                try:
                    # Tenta enviar um ping ao servidor para verificar se está ativo
                    client_socket.send(b"")
                except Exception as e:
                    print("[Erro]: Servidor não responde. Você será promovido a servidor.")
                    # Verifique se já houve uma promoção
                    if not is_promoted:
                        is_promoted = True
                        client_socket.close()
                        # Iniciar o servidor local
                        start_server('localhost', server_port)
                    return
                
                time.sleep(5)

        # Inicia a thread para monitorar a conexão com o servidor
        monitor_thread = threading.Thread(target=monitor_server_connection)
        monitor_thread.start()

        # Inicia a thread para receber mensagens
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, server_ip))
        receive_thread.start()

        # Inicia a thread para enviar mensagens
        send_thread = threading.Thread(target=send_message, args=(client_socket,))
        send_thread.start()
    except Exception as e:
        print("[Erro]:", e)
        client_socket.close()

# Função para iniciar o servidor
def start_server(host, port):
    global server_host, server_port, is_promoted
    server_host = host
    server_port = port
    is_promoted = True  # Marca que um servidor já foi iniciado
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print("Servidor aguardando conexões...")

        def accept_connections():
            while not shutdown_event.is_set():
                try:
                    client_socket, client_address = server_socket.accept()
                    client_sockets.append(client_socket)
                    print(f"Conexão estabelecida com {client_address}")
                    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, client_address))
                    receive_thread.start()
                except OSError as e:
                    if shutdown_event.is_set():
                        print("Parando a thread de aceitação de conexões.")
                        break
                    else:
                        print("[Erro]:", e)

        accept_thread = threading.Thread(target=accept_connections)
        accept_thread.start()

        while True:
            command = input("Digite 'desligar' para encerrar o servidor: ")
            if command.lower() == "desligar":
                shutdown_server(server_socket)
                break

    except Exception as e:
        print("[Erro]:", e)
    finally:
        server_socket.close()

# Função para escolher entre ser servidor ou cliente
def choose_role():
    while True:
        role = input("Digite 's' para servidor ou 'c' para cliente: ")
        if role.lower() == 's':
            host_server = input("Digite o IP do servidor ou 'localhost' se for na mesma máquina: ")
            if host_server.lower() == 'localhost':
                host_server = 'localhost'
            port = int(input("Digite a porta para o servidor: "))
            start_server(host_server, port)
            break
        elif role.lower() == 'c':
            server_ip = input("Digite o IP do servidor (ou 'localhost' se for na mesma máquina): ")
            if server_ip.lower() == 'localhost':
                server_ip = 'localhost'
            server_port = int(input("Digite a porta do servidor: "))
            start_client(server_ip, server_port)
            break
        else:
            print("Opção inválida. Digite 's' ou 'c'.")

if __name__ == "__main__":
    choose_role()
