import socket 
import time  

# Tamanho da mensagem fixa em bytes
F = 10

# Função principal que simula o processo
def main(process_id, num_repetitions, delay):
    # Cria um socket para comunicação via TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Conecta o socket ao coordenador (servidor)
    client_socket.connect(('localhost', 5000))
    
    # Loop para realizar as requisições à região crítica
    for _ in range(num_repetitions):
        # Envia uma mensagem REQUEST ao coordenador
        request_msg = f"REQUEST|{process_id}".ljust(F)
        client_socket.send(request_msg.encode('utf-8'))
        
        # Recebe a resposta do coordenador (GRANT)
        grant_msg = client_socket.recv(F).decode('utf-8')
        
        # Se receber GRANT, acessa a região crítica
        if "GRANT" in grant_msg:
            print(f"Process {process_id} granted access")
            
            # Abre o arquivo resultado.txt para escrita (modo append)
            with open('resultado.txt', 'a') as file:
                # Escreve o ID do processo e o timestamp atual no arquivo
                file.write(f"Process {process_id}: {time.time()}\n")
            
            # Aguarda alguns segundos simulando a execução na região crítica
            time.sleep(delay)
        
        # Envia uma mensagem RELEASE ao coordenador, liberando a região crítica
        release_msg = f"RELEASE|{process_id}".ljust(F)
        client_socket.send(release_msg.encode('utf-8'))
    
    # Fecha a conexão do socket ao finalizar o loop
    client_socket.close()

if __name__ == "__main__":
    # IDs dos processos, número de repetições e atraso em segundos
    main(process_id=1, num_repetitions=5, delay=1)
