import subprocess
import time
import random

# IDs dos processos
process_ids = [1, 2, 3]

# Embaralha a ordem dos processos
random.shuffle(process_ids)

# Inicia o coordenador
subprocess.Popen(['python', 'coordenador.py'])

time.sleep(2)  # Aguarda o coordenador iniciar

# Inicia os processos em ordem aleatória
for process_id in process_ids:
    subprocess.Popen(['python', 'processo.py', str(process_id), '5', '1'])
    time.sleep(1)  # Aguarda um segundo entre as execuções dos processos
