import numpy as np


import os
import sys

# Descobre o caminho da pasta onde o arnold_melhorado.py está (matrizes_operations)
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Adiciona essa pasta ao mapa de busca do Python se ela já não estiver lá
if diretorio_atual not in sys.path:
    sys.path.append(diretorio_atual)

# AGORA SIM o seu import original vai funcionar perfeitamente:
from util import *







def arnold_fast(img_array, k , matriz_base=None):
    """_summary_

    Args:
        img_array (_np.ndarray_): _imagem em array_
        k (_int_): _chave de criptografia -> chave única_
        matriz_base (_np.ndarray_, optional): _é a matriz base da criptografia, mas é  aconselhavel deixar a matriz base de fibonacci criada na função_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    n = img_array.shape[0]
    # Cria matrizes de índices x e y: [[0,1,2...], [0,1,2...]]
    x, y = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    
    if matriz_base is None:
        matriz_base = np.array([[1, 1],
                      [1, 2]])
    M = expoente_modular(matriz_base, k, n)
    # Aplica a fórmula diretamente nos arrays (vetorização)
    #x_novo = (2x + y) % n
    
    #y_novo = (x + y) % n
    #nx = (x + y) % n
    #ny = (x + 2*y) % n
    nx = (M[0, 0] * x + M[0, 1] * y) % n
    ny = (M[1, 0] * x + M[1, 1] * y) % n
    return img_array[nx, ny]

def decript_arnold(img_array, k , matriz_base=None):
    """_summary_

    Args:
        img_array (_np.ndarray_): _imagem em array_
        k (_int_): _é o valor chave de criptografia -> chave única_
        matriz_base (_np.ndarray_, optional): _é a matriz base feita na criptografia, é aconselhavel deixar a função fazer o trabalho_. Defaults to None.

    Returns:
        _type_: _description_
    """
    n = img_array.shape[0]
    
    x, y = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    
    if matriz_base is None:
        matriz_base = np.array([[1, 1],
                                [1, 2]])
    p = periodo(matriz_base, n) #periodo dde Paincaré
    
    M = expoente_modular(matriz_base, abs(p - k), n)
    
    nx = (M[0, 0] * x + M[0, 1] * y) % n
    ny = (M[1, 0] * x + M[1, 1] * y) % n
    #nx = (2*x - y) % n
    #ny = (-x + y) % n
    
    return img_array[nx, ny]



