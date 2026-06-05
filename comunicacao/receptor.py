import socket
import sys
from PIL import Image
import io
import os

from pathlib import Path

# Define a pasta raiz do projeto de forma robusta
raiz_projeto = Path(__file__).resolve().parent.parent

if str(raiz_projeto) not in sys.path:
    sys.path.append(str(raiz_projeto))

from diffie_hellman import dh
from matrizes_operations.util import *
from matrizes_operations.difusao import *
from matrizes_operations.arnold_melhorado import *


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


if len(sys.argv) < 2 or not sys.argv[1].isdigit():
    print("Erro: porta inválida ou não informada.")
    print("Uso: python3 receptor.py <PORTA>")
    print("Exemplo: python3 receptor.py 1234")
    sys.exit(1)

PORTA = int(sys.argv[1])
HOST = '0.0.0.0'

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORTA))
servidor.listen(1)

socket_cliente = None

try:
    print(f"[*] Receptor aguardando conexão na porta {PORTA}...")

    socket_cliente, endereco_cliente = servidor.accept()
    print(f"[+] Conexão estabelecida com: {endereco_cliente}")

    # 1. Gera e envia a chave pública do receptor primeiro
    chave_privada = dh.gerar_chave_privada()
    chave_publica = dh.calcular_chave_publica(chave_privada)
    enviar_mensagem(socket_cliente, chave_publica)

    # 2. Recebe a chave pública do emissor
    chave_publica_emissor = int(receber_mensagem(socket_cliente))

    # 3. Calcula o segredo compartilhado
    chave_secreta = dh.calcular_segredo_compartilhado(chave_privada, chave_publica_emissor)
    print("[+] Chave secreta estabelecida.")

    # --- Recebimento da imagem ---
    # 4. Recebe o tamanho esperado do arquivo
    tamanho_esperado = int(receber_mensagem(socket_cliente))
    print(f"[*] Aguardando imagem ({tamanho_esperado} bytes)...")

    # 5. Recebe os bytes da imagem em loop até completar
    dados_img = b""
    while len(dados_img) < tamanho_esperado:
        restante = tamanho_esperado - len(dados_img)
        pedaco = socket_cliente.recv(min(4096, restante))
        if not pedaco:
            break
        dados_img += pedaco

    print(f"[+] Imagem recebida ({len(dados_img)} bytes).")

    img_recebida = Image.open(io.BytesIO(dados_img))
    img_array = np.array(img_recebida)
    
    img_undifundir = decifrar_com_chave_dh(img_array, chave_secreta)
    img_unconfundir = decript_arnold(img_undifundir, chave_secreta)
    
    recuperar_imagem(img_unconfundir).show()

except Exception as e:
    print(f"[-] Ocorreu um erro no servidor: {e}")

finally:
    if socket_cliente:
        socket_cliente.close()
    servidor.close()
    print("[*] Servidor finalizado.")