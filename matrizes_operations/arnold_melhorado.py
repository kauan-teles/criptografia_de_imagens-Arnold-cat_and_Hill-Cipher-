from PIL import Image
import numpy as np

def arnold_fast(img_array):
    n = img_array.shape[0]
    # Cria matrizes de índices x e y: [[0,1,2...], [0,1,2...]]
    x, y = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    
    # Aplica a fórmula diretamente nos arrays (vetorização)
    # x_novo = (2x + y) % n
    # y_novo = (x + y) % n
    nx = (x + y) % n
    ny = (x + 2*y) % n
    
    return img_array[nx, ny]

def decript_arnold(img_array):
    n = img_array.shape[0]
    x, y = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    nx = (2*x - y) % n
    ny = (-x + y) % n
    
    return img_array[nx, ny]

def recuperar_imagem(img_array):
    # Converte o array do numpy (uint8) de volta para uma imagem PIL
    # O modo 'RGB' garante que as cores sejam interpretadas corretamente
    img_final = Image.fromarray(img_array.astype(np.uint8), 'RGB')
    return img_final

# Exemplo de uso:
# 1. Transforma imagem em array
img_original = Image.open('x.png').convert('RGB')
arr = np.array(img_original)

# 2. Processa (usando a função rápida que discutimos)
n = arr
for x in range(25):
    n = decript_arnold(n)

rec = recuperar_imagem(n)
rec.show()