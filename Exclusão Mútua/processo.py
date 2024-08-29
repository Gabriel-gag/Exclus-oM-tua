import socket
import time
import sys

# Tamanho da mensagem fixa em bytes
F = 10

def process_task(process_id, num_repetitions, delay):
    """Função que simula o processo com comunicação via sockets."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Conecta o socket ao coordenador (servidor)
        client_socket.connect(('localhost', 5000))
        
        for _ in range(num_repetitions):
            # Envia uma mensagem REQUEST ao coordenador
            request_msg = f"REQUEST|{process_id}".ljust(F)
            client_socket.send(request_msg.encode('utf-8'))
            
            # Recebe a resposta do coordenador (GRANT)
            try:
                grant_msg = client_socket.recv(F).decode().strip()
                if "GRANT" in grant_msg:
                    print(f"Process {process_id} granted access")
                    
                    # Abre o arquivo resultado.txt para escrita (modo append)
                    with open('resultado.txt', 'a') as file:
                        file.write(f"Process {process_id}: {time.time()}\n")
                    
                    # Aguarda alguns segundos simulando a execução na região crítica
                    time.sleep(delay)
                
                # Envia uma mensagem RELEASE ao coordenador, liberando a região crítica
                release_msg = f"RELEASE|{process_id}".ljust(F)
                client_socket.send(release_msg.encode('utf-8'))
            
            except ConnectionResetError:
                print(f"Process {process_id} connection was reset by the server.")
                break

    finally:
        # Fecha a conexão do socket ao finalizar o loop
        client_socket.close()

if __name__ == "__main__":
    # Obtém argumentos da linha de comando
    process_id = int(sys.argv[1])
    num_repetitions = int(sys.argv[2])
    delay = int(sys.argv[3])
    
    # Executa a tarefa do processo
    process_task(process_id, num_repetitions, delay)
