from PIL import Image

# 1. Criar uma imagem nova (largura, altura) com fundo preto
largura, altura = 100, 100
img = Image.new('RGB', (largura, altura), "black")

# 2. Construir a imagem pixel a pixel (criando um padrão xadrez)
for x in range(largura):
    for y in range(altura):
        # Define a cor baseada na posição
        if (x + y) % 2 == 0:
            img.putpixel((x, y), (255, 255, 255)) # Branco
        else:
            img.putpixel((x, y), (255, 0, 0)) # Vermelho

# 3. Salvar ou mostrar a imagem
img.show()
img.save('imagem_pixelada.png')
