import socket
import sys
import io
import os
from pathlib import Path

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, "..", ".."))
if raiz_projeto not in sys.path:
    sys.path.insert(0, raiz_projeto)

from aplication.diffie_hellman import dh
from aplication.matrizes_operations.util import *
from aplication.matrizes_operations.arnold_melhorado import *
from aplication.matrizes_operations.difusao import *

if len(sys.argv) < 4 or not sys.argv[3].isdigit():
    print("Erro: Parâmetros insuficientes ou incorretos.")
    print("Modo de uso: python3 emissor.py <CAMINHO_IMAGEM> <IP_RECEPTOR> <PORTA>")
    print("Exemplo:    python3 emissor.py aplication/deadpool.png 127.0.0.1 1234")
    sys.exit(1)



def receber_mensagem(sock):
    """Recebe uma mensagem delimitada por newline '\n'."""
    dados = b""
    while not dados.endswith(b"\n"):
        byte = sock.recv(1)
        if not byte:
            break
        dados += byte
    return dados.decode("utf-8").strip()


def enviar_mensagem(sock, msg):
    """Envia uma mensagem delimitada por newline '\n'."""
    sock.sendall((str(msg) + "\n").encode("utf-8"))



CAMINHO_IMAGEM = sys.argv[1]
IP_ALVO = sys.argv[2]
PORTA_ALVA = int(sys.argv[3])

if not os.path.exists(CAMINHO_IMAGEM) or not Path(CAMINHO_IMAGEM).is_file():
    print(f"Erro: O arquivo de imagem '{CAMINHO_IMAGEM}' não foi encontrado!")
    sys.exit(1)

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print(f"[*] Conectando a {IP_ALVO}:{PORTA_ALVA}...")
    cliente.connect((IP_ALVO, PORTA_ALVA))
    print("[+] Conectado com sucesso ao receptor!")
    
    # 1. Recebe a chave pública do receptor
    chave_publica_receptor = int(receber_mensagem(cliente))

    # 2. Envia a chave pública do emissor e gera a chave privada local
    chave_privada = dh.gerar_chave_privada()
    chave_publica = dh.calcular_chave_publica(chave_privada)
    enviar_mensagem(cliente, chave_publica)

    # 3. Calcula o segredo compartilhado
    chave_secreta = dh.calcular_segredo_compartilhado(chave_privada, chave_publica_receptor)
    print("[+] Chave secreta estabelecida.")

    # --- Criptografia e envio da imagem ---
    imagem = image_to_array(CAMINHO_IMAGEM)

    img_confundida = arnold_fast(imagem, chave_secreta)
    img_difundida = cifrar_com_chave_dh(img_confundida, chave_secreta)

    img_criptografada = recuperar_imagem(img_difundida)
    buffer_bytes = io.BytesIO()
    img_criptografada.save(buffer_bytes, format='PNG')
    bytes_da_imagem = buffer_bytes.getvalue()

    # 4. Envia o tamanho do arquivo antes dos dados
    tamanho = len(bytes_da_imagem)
    enviar_mensagem(cliente, tamanho)
    print(f"[*] Enviando imagem ({tamanho} bytes)...")

    # 5. Envia os bytes da imagem
    cliente.sendall(bytes_da_imagem)
    print("[+] Imagem enviada com sucesso!")

except Exception as e:
    print(f"[-] Ocorreu um erro na conexão: {e}")

finally:
    cliente.close()
    print("[*] Cliente finalizado.")