import random
import subprocess
import time

#ID dos processos
processo_ids=[1,2,3]

random.shuffle(processo_ids)

# Inicia o coordenador
subprocess.Popen(['python', 'coordenador.py'])

time.sleep(2)  # Aguarda o coordenador iniciar

# Inicia os processos
for i in range(1, 4):
    subprocess.Popen(['python', 'processo.py', str(processo_ids), '5', '1'])
    time.sleep(1)  # Aguarda um segundo entre as execuções dos processos
