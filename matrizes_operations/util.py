from PIL import Image
import numpy as np


def periodo(matriz_base, n):
    current = matriz_base.copy()
    I = np.eye(2, dtype=int)  # Matriz Identidade 2x2
    passos = 1
    
    # Loop multiplicando a matriz 2x2 e aplicando o módulo n
    while not np.array_equal(current, I):
        current = np.dot(current, matriz_base) % n
        passos += 1
    print(passos)
    return passos
    
    
def expoente_modular(A, k, n):
    t = A.shape[0]
    result = np.identity(t, dtype=int)
    base = A.astype(object)
    
    while k > 0:
        if k % 2 == 1:
            result = np.dot(result, base) % n
        base = np.dot(base,base) % n
        k//=2
    return result.astype(int)            
    
def recuperar_imagem(img_array):
    # Converte o array do numpy (uint8) de volta para uma imagem PIL
    # O modo 'RGB' garante que as cores sejam interpretadas corretamente
    img_final = Image.fromarray(img_array.astype(np.uint8), 'RGB')
    return img_final


def inverso_modular_det(det, m=256):
    """Acha o inverso do determinante no módulo 256."""
    det = det % m
    for x in range(1, m):
        if (det * x) % m == 1:
            return x
    raise ValueError("Determinante não possui inverso (não é ímpar).")

def calcular_inversa(matriz):
    """Calcula a inversa modular 3x3 de forma simples e direta."""
    # 1. Calcular o determinante inteiro
    det = int(round(np.linalg.det(matriz)))
    inv_det = inverso_modular_det(det, 256)
    
    # 2. O truque clássico da Álgebra Linear para achar a Adjunta:
    # A matriz inversa tradicional é (1/det) * Adjunta.
    # Portanto, se multiplicarmos a inversa tradicional pelo det, sobra a Adjunta!
    inversa_tradicional = np.linalg.inv(matriz)
    adjunta = np.round(inversa_tradicional * det).astype(int)
    
    # 3. Multiplicar o inverso do determinante pela adjunta no módulo 256
    matriz_inversa_modular = (inv_det * adjunta) % 256
    
    return matriz_inversa_modular.astype(np.uint8)

def image_to_array(path, quadrada=True):
    
    try:
        img = Image.open(path).convert('RGB')
        if quadrada:
            img = img.resize((min(img.size), min(img.size)))
        img_array = np.array(img)
        return img_array
    except:
        print("Impossivel carregar a imagem")
        return False

def alterar_imagem_pixel_save(path):
    import random
    import re
    
    imagem_original = image_to_array(path)
    img = imagem_original.copy()
    n = img.shape[0]
    x = random.randint(0, n-1)
    y = random.randint(0, n-1)
    r, g, b = map(int, img[x][y])
    R = (r*r+g) % 256
    G = (r*g + b) % 256
    B = (b*3*r + g) % 256
    img[x, y] = (R, G, B)
    newpath = path.replace(".png", "_modificada_pixel.png")
    recuperar_imagem(img).save(newpath)
    
    
    
if __name__ == '__main__':
    matriz = np.array([[1, 0],[0, 3]])
    print(periodo(matriz, 250))
