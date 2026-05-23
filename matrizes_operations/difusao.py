from PIL import Image
import numpy as np
from aplication.matrizes_operations.util import *

def gerar_matriz_hill_valida(chave_dh):
    """
    Gera uma matriz 3x3 inteira a partir da chave Diffie-Hellman
    garantindo que ela seja inversível no módulo 256.
    """
    # 1. Usamos a chave do DH como semente do gerador pseudoaleatório.
    # Como a semente é a mesma, emissor e receptor criarão a mesma sequência!
    # Convertemos para string e depois pegamos o hash/inteiro se for muito grande
    semente = int(chave_dh) % (2**32 - 1)
    rng = np.random.default_rng(semente)
    
    while True:
        # Gerar 9 números aleatórios entre 0 e 255 para preencher a matriz 3x3
        matriz = rng.integers(0, 256, size=(3, 3))
        
        # Calcular o determinante arredondado para inteiro
        det = int(round(np.linalg.det(matriz)))
        det_mod_256 = det % 256
        
        # REGRA CRÍTICA DE ALGEBRA: 
        # O mdc(det_mod_256, 256) precisa ser 1. Como 256 só divide por potências de 2,
        # o determinante no módulo 256 precisa ser apenas um NÚMERO ÍMPPAR e diferente de 0.
        if det_mod_256 != 0 and det_mod_256 % 2 != 0:
            return matriz
        # Se não for ímpar, o 'while' continua e o gerador cria outra de forma determinística

def cifrar_com_chave_dh(img_array, chave_dh):
    # 1. Abre a imagem com o PIL
    
    img_np = img_array
    linhas, colunas, canais = img_np.shape
    
    # 2. Cria a matriz chave dinamicamente usando o segredo compartilhado
    K = gerar_matriz_hill_valida(chave_dh)
    print("Matriz Hill Gerada Dinamicamente:\n", K)
    
    # 3. Vetorização para aplicar a Cifra de Hill sem usar laços 'for'
    pixels_vetorizados = img_np.reshape(-1, 3)
    pixels_cifrados = np.dot(pixels_vetorizados, K.T) % 256
    
    # 4. Reconstrói a imagem
    img_cifrada_np = pixels_cifrados.reshape(linhas, colunas, 3)
    return img_cifrada_np


def decifrar_com_chave_dh(img_array, chave_dh):
    # 1. Garante que a imagem seja tratada como inteiros de 64 bits para evitar overflow
    img_np = img_array.astype(np.int64)
    linhas, colunas, canais = img_np.shape
    
    # 2. Gera a matriz de Hill 3x3 a partir da chave Diffie-Hellman
    matriz_original = gerar_matriz_hill_valida(chave_dh)
    
    # 3. Calcula a matriz inversa modular (garantindo que seja int64)
    K_inversa = calcular_inversa(matriz_original).astype(np.int64)
    
    # 4. Vetoriza os pixels da imagem para o formato (N, 3)
    pixels_vetorizados = img_np.reshape(-1, 3)
    
    # 5. Aplica a multiplicação pela matriz inversa e tira o módulo 256
    # Como tudo é int64, o resultado intermediário não estoura a memória
    pixels_decifrados = np.dot(pixels_vetorizados, K_inversa.T) % 256
    
    # 6. Reconstrói o array no formato original da imagem e converte para uint8
    img_decifrada_np = pixels_decifrados.reshape(linhas, colunas, 3).astype(np.uint8)
    
    # 7. Retorna o objeto de Imagem do Pillow pronto para ser exibido
    return img_decifrada_np


# Suponha que o cálculo do Diffie-Hellman resultou neste número secreto compartilhado:
chave_secreta_dh = 983471298347192384712394817239481273912839

# Executa a difusão
if __name__ == "__main__":
    img = np.array(Image.open('aplication/deadpool.png'))
    imagem_resultado = cifrar_com_chave_dh(img, chave_secreta_dh)
    recuperar_imagem(imagem_resultado).show()