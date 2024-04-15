import socket
import threading

identification = input("Como você deseja ser identificado? ")
# Evento para sinalizar desligamento
shutdown_event = threading.Event()
# Variável global para o socket do cliente
client_socket = None
# Lista para armazenar os sockets dos clientes conectados
client_sockets = []

# Função para receber mensagens do cliente
def receive_messages(client_socket, client_address):
    while True:
        try:
            # Recebe a mensagem do cliente e a imprime
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
            # Envie a mensagem recebida para todos os outros clientes
            for client in client_sockets:
                if client != client_socket:
                    client.send(message.encode('utf-8'))
        except Exception as e:
            print("[Erro]:", e)
            break

# Função para enviar mensagem
def send_message(client_socket):
    while True:
        message = input()
        try:
            client_socket.send(f"{identification}: {message}".encode('utf-8'))
            # Se o cliente digitar "/sair", a conexão é encerrada
            if message.lower() == "/sair":
                client_socket.close()
                break
        except Exception as e:
            print("[Erro]:", e)
            break


def shutdown_server(server_socket):
    print("Desligando o servidor...")

    # Sinaliza o desligamento para as threads
    shutdown_event.set()

    # Fechar todos os sockets dos clientes
    for client_socket in client_sockets:
        try:
            client_socket.close()
        except Exception as e:
            print("[Erro ao fechar socket do cliente]:", e)

    # Fechar o socket do servidor
    server_socket.close()

    # Imprimir mensagem de confirmação
    print("Servidor desligado com sucesso.")


# Função para iniciar a conexão como cliente
def start_client(server_ip, server_port):
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print("Conectado ao servidor.")
        # Inicia a thread para receber mensagens
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, server_ip))
        receive_thread.start()
        # Inicia a thread para enviar mensagens
        send_thread = threading.Thread(target=send_message, args=(client_socket,))
        send_thread.start()
    except Exception as e:
        print("[Erro]:", e)
        client_socket.close()



def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global client_socket
    try:
        # Liga o socket ao host e porta especificados
        server_socket.bind((host, port))
        # Coloca o socket em modo de escuta
        server_socket.listen(5)
        print("Servidor aguardando conexões...")

        # Thread para aceitar conexões
        def accept_connections():
            while not shutdown_event.is_set():
                try:
                    # Aceita conexão do cliente
                    client_socket, client_address = server_socket.accept()
                    client_sockets.append(client_socket)  # Adiciona o novo cliente à lista
                    print(f"Conexão estabelecida com {client_address}")
                    # Inicia a thread para receber mensagens
                    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, client_address))
                    receive_thread.start()
                except OSError as e:
                    if shutdown_event.is_set():
                        print("Parando a thread de aceitação de conexões.")
                        break
                    else:
                        print("[Erro]:", e)

        # Inicia a thread para aceitar conexões
        accept_thread = threading.Thread(target=accept_connections)
        accept_thread.start()

        # Loop para monitorar entrada do usuário
        while True:
            command = input("Digite 'desligar' para encerrar o servidor: ")
            if command.lower() == "desligar":
                # Chama a função de desligar o servidor
                shutdown_server(server_socket)
                break

    except Exception as e:
        print("[Erro]:", e)
    finally:
        # Certifique-se de fechar o socket do servidor
        server_socket.close()


# Função para escolher entre ser servidor ou cliente
def choose_role():
    while True:
        role = input("Digite 's' para servidor ou 'c' para cliente: ")
        if role.lower() == 's':
            host_server = input("digite o ip do seu servidor ou 'localhost' se for na mesma maquina ")
            if host_server.lower() == 'localhost':
                host_server = 'localhost'
            start_server(host_server, int(input("Digite a porta para o servidor: ")))
            break
        elif role.lower() == 'c':
            server_ip = input("Digite o IP do servidor (ou 'localhost' se for na mesma máquina): ")
            if server_ip.lower() == 'localhost':
                server_ip = 'localhost'
            start_client(server_ip, int(input("Digite a porta do servidor: ")))
            break
        else:
            print("Opção inválida. Digite 's' ou 'c'.")

if __name__ == "__main__":
    choose_role()
