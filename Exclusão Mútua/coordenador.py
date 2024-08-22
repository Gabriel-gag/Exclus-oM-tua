import socket 
import threading  
import queue  
import time  

# Tamanho da mensagem fixa em bytes
F = 10

# Fila para armazenar os pedidos de acesso à região crítica
request_queue = queue.Queue()

# Dicionário para armazenar a contagem de acessos de cada processo
access_count = {}

#Lock para proteger acesso ao log
log_lock=threading.Lock()

# Função que lida com as requisições de cada processo
def handle_request(client_socket, client_address):
    while True:
        try:
            message = client_socket.recv(F).decode('utf-8').strip()
            
            if not message:
                break
            
            if message.startswith("REQUEST"):
                process_id = message.split("|")[1].strip()
                with log_lock:
                    request_queue.put(process_id)
                print(f"Received REQUEST from process {process_id}")
                
                # Concede acesso enviando GRANT
                client_socket.send(f"GRANT|{process_id}".ljust(F).encode('utf-8'))
                
                with log_lock:
                    access_count[process_id] = access_count.get(process_id, 0) + 1

            elif message.startswith("RELEASE"):
                process_id = message.split("|")[1].strip()
                with log_lock:
                    if not request_queue.empty():
                        request_queue.get()
                print(f"Received RELEASE from process {process_id}")
        
        except socket.error:
            break

    client_socket.close()

# Função para lidar com os comandos do terminal (interface do coordenador)
def interface_thread():
    while True:
        command = input("Enter command (1: print queue, 2: print access count, 3: exit): ")
        
        if command == "1":
            with log_lock:
                print(f"Queue: {list(request_queue.queue)}")
        
        elif command == "2":
            with log_lock:
                print(f"Access Count: {access_count}")
        
        elif command == "3":
            print("Shutting down coordinator.")
            exit(0)  # Encerrar o coordenador e todos os processos

# Função principal que inicia o servidor (coordenador)
def main():
    # Cria um socket para comunicação via TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Associa o socket a um endereço IP e porta
    server_socket.bind(('localhost', 5000))
    
    # Configura o socket para escutar conexões (até 5 simultâneas)
    server_socket.listen(5)

    # Inicia a thread para a interface do terminal
    threading.Thread(target=interface_thread).start()

    # Loop principal para aceitar conexões de novos processos
    while True:
        # Aceita uma nova conexão
        client_socket, client_address = server_socket.accept()
        
        # Inicia uma nova thread para lidar com o processo conectado
        threading.Thread(target=handle_request, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    main()  # Executa o coordenador
