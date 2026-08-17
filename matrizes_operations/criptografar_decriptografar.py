from PIL import Image
import numpy as np
import os
import sys
import time
from functools import wraps
from pathlib import Path

# Define a pasta raiz do projeto de forma robusta
raiz_projeto = Path(__file__).resolve().parent.parent

if str(raiz_projeto) not in sys.path:
    sys.path.append(str(raiz_projeto))

from matrizes_operations.difusao import cifrar_com_chave_dh, decifrar_com_chave_dh, difusao_avalanche, dedifusao_avalanche
from matrizes_operations.arnold_melhorado import arnold_fast, decript_arnold
from matrizes_operations.util import *

def medir_tempo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        result = func(*args, **kwargs)
        fim = time.perf_counter()
        print(f"A função '{func.__name__}' levou {fim - inicio:.4f} segundos para executar.")
        return result
    return wrapper


def criptografar(img, key):
    img_arnold = arnold_fast(img, key)
    img_hill = cifrar_com_chave_dh(img_arnold, key)
    return difusao_avalanche(img_hill)

def decriptografar(img_array, key):
    img_unavalanche = dedifusao_avalanche(img_array)
    img_unhill = decifrar_com_chave_dh(img_unavalanche, key)
    return decript_arnold(img_unhill, key)



if __name__ == "__main__":
    from diffie_hellman.dh import *
    name = "Lenna"
    path = f"/home/kauan-teles/Documentos/Algebra-Linear/aplication/imagens/{name}/{name}.png"
    img = image_to_array(path)
    cript = criptografar(img, gerar_chave_privada())
    recuperar_imagem(cript).show()
    