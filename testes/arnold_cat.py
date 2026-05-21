import numpy as np
from PIL import Image

#Esse é o array que representa a matriz padrão fibonacci para o gato de Arnold
A = np.array([[2, -1],
              [-1, 1]])

def expoente(matriz, K):
    X = matriz
    for n in range(K-1):
        X = np.dot(X, matriz)
    return X

#Aplicação do gato de Arnold, fase teste, o código não está nem perto do que eu quero.

print(expoente(A, 25))
try:
    img = Image.open('x.png')
    print(img.format, img.size)
    
    largura, altura = img.size
    ng = Image.new('RGB', img.size, color='black')
    R = expoente(A, 25)
    for x in range(largura):
        for y in range(altura):
            j = np.array([x, y])
            produto = np.dot(R, j) % (largura-1)
            
            ng.putpixel((x, y), img.getpixel(produto))
            
            
            
            
        
    ng.show()
    
except IOError:
    print("Erro")
    
