from PIL import Image
import numpy as np
def periodo(A, n):
    if (not isinstance(A, np.ndarray)):
        return -1 #A não é uma matriz
    I = np.identity(2, dtype=int)
    current = A.copy()
    k = 1
    while (not np.array_equal(current % n, I)):
        current = np.dot(current, A)
        k+=1
        
        if k > n*n:
            return -1
    return k
    
    
def expoente_modular(A, k, n):
    result = np.identity(2, dtype=int)
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