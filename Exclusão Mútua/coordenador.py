import socket
import threading
import queue
import time
from datetime import datetime

# Configurações do coordenador
HOST = '127.0.0.1'  # Endereço IP do coordenador
PORT = 5000         # Porta do coordenador

# Fila de pedidos para a região crítica
request_queue = queue.Queue()

# Contador de acessos por processo
access_count = {}

# Lock para garantir acesso sincronizado à fila e contador
lock = threading.Lock()

# Arquivo de log
log_file = open('coordinator_log.txt', 'a')

def log_message(message):
    """Função para registrar mensagens no log com timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_file.write(f"[{timestamp}] {message}\n")
    log_file.flush()

def handle_client(client_socket, process_id):
    """Função que lida com o algoritmo de exclusão mútua para cada processo."""
    global access_count

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            if "REQUEST" in message:
                log_message(f"Recebido REQUEST do processo {process_id}")
                with lock:
                    request_queue.put(process_id)
                
                # Processa o pedido se for o próximo na fila
                with lock:
                    if request_queue.queue[0] == process_id:
                        grant_message = "GRANT"
                        client_socket.send(grant_message.encode())
                        log_message(f"Enviado GRANT ao processo {process_id}")
                        
                        # Registra o acesso
                        access_count[process_id] = access_count.get(process_id, 0) + 1

            elif "RELEASE" in message:
                log_message(f"Recebido RELEASE do processo {process_id}")
                with lock:
                    request_queue.get()
                
                # Se houver outros pedidos na fila, concede acesso ao próximo
                with lock:
                    if not request_queue.empty():
                        next_process = request_queue.queue[0]
                        next_socket = process_sockets[next_process]
                        next_socket.send("GRANT".encode())
                        log_message(f"Enviado GRANT ao processo {next_process}")

        except ConnectionResetError:
            print(f"Processo {process_id} desconectado.")
            break

    client_socket.close()

def accept_connections(server_socket):
    """Função para aceitar conexões dos processos."""
    while True:
        client_socket, _ = server_socket.accept()
        process_id = len(process_sockets) + 1  # Atribui um ID único para cada processo
        process_sockets[process_id] = client_socket
        print(f"Processo {process_id} conectado.")
        log_message(f"Processo {process_id} conectado.")
        threading.Thread(target=handle_client, args=(client_socket, process_id)).start()

def interface():
    """Função que lida com os comandos da interface."""
    while True:
        command = input("Comando (1: Imprimir fila, 2: Imprimir acessos, 3: Encerrar): ")

        if command == '1':
            with lock:
                print(f"Fila de pedidos atual: {list(request_queue.queue)}")
        
        elif command == '2':
            with lock:
                for pid, count in access_count.items():
                    print(f"Processo {pid} foi atendido {count} vezes.")

        elif command == '3':
            print("Encerrando o coordenador.")
            log_message("Coordenador encerrado.")
            break

if __name__ == "__main__":
    # Cria o socket do coordenador
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Coordenador escutando em {HOST}:{PORT}")
    log_message(f"Coordenador iniciado em {HOST}:{PORT}")

    process_sockets = {}

    # Inicia a thread para aceitar conexões dos processos
    threading.Thread(target=accept_connections, args=(server_socket,)).start()

    # Inicia a thread da interface
    interface_thread = threading.Thread(target=interface)
    interface_thread.start()

    # Espera a interface finalizar
    interface_thread.join()

    # Fecha o socket do coordenador e o arquivo de log
    server_socket.close()
    log_file.close()
