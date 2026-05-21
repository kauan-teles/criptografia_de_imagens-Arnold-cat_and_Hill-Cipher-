import numpy as np
from PIL import Image
from matrizes_operations import arnold_melhorado
from matrizes_operations import difusao


from matrizes_operations.util import *



k = 60000

img_array = np.array(Image.open('aplication/deadpool_criptografado.png'))
img_result = arnold_melhorado.decript_arnold(img_array, k)

x = difusao.decifrar_com_chave_dh(img_result, k)
recuperar_imagem(img_result).show()