import numpy as np
import math

# Definição de duas matrizes
A = np.array([[1, 2],
              [3, 4]])

B = np.array([[5, 6],
              [7, 8]])

# 1. Soma de matrizes
soma = A + B
print("Soma de A e B:\n", soma)

# 2. Multiplicação por escalar
escalar = 3
mult_escalar = escalar * A
print("\nA multiplicada por escalar 3:\n", mult_escalar)

# 3. Multiplicação de matrizes
mult_matrizes = np.dot(A, B)
print("\nMultiplicação de A e B:\n", mult_matrizes)

# 4. Exemplo com matriz 3x3 (para simular Hill)
H = np.array([[2, 1, 0],
              [1, 1, 1],
              [0, 1, 2]])

pixel = np.array([10, 20, 30])  # vetor RGB

# Multiplicação matriz x vetor
novo_pixel = np.dot(H, pixel)
print("\nPixel transformado por H:\n", novo_pixel)

# 5. Multiplicação por escalar usando traço da matriz
traco_A = np.trace(A)  # soma da diagonal principal
H_mod = traco_A * H
print("\nMatriz H modificada pelo traço de A:\n", H_mod)

novo_pixel_mod = np.dot(H_mod, pixel)
determinanteB = math.trunc(np.linalg.det(B))
print("\nDeterminante de B = ", determinanteB)
determinanteA = math.trunc(np.linalg.det(A))
print("\nDeterminante de A = ", determinanteA)
print("\nPixel transformado por H_mod:\n", novo_pixel_mod)
