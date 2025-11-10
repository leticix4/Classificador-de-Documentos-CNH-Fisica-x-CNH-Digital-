import cv2
import albumentations as A
import os
import numpy as np

pasta_entrada = "cnh_digital/imagens_geradas"
pasta_saida = "cnh_digital/imagens_transformadas"
os.makedirs(pasta_entrada, exist_ok=True)
os.makedirs(pasta_saida, exist_ok=True)

aumentacoes = A.Compose([
    A.LongestMaxSize(max_size=800, p=1.0),  
    A.PadIfNeeded(min_height=600, min_width=800, border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255), p=1.0),
    A.Rotate(limit=3, p=0.5, border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255)),
    
    A.RandomBrightnessContrast(
        brightness_limit=0.1,
        contrast_limit=0.1,
        p=0.3
    ),
    
    A.Perspective(scale=(0.02, 0.05), p=0.3),
])

aumentacoes_quase_original = A.Compose([
    A.LongestMaxSize(max_size=800, p=1.0),
    A.PadIfNeeded(min_height=600, min_width=800, border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255), p=1.0),
    A.Rotate(limit=1, p=0.3, border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255)),
])

arquivos = [f for f in os.listdir(pasta_entrada) if f.endswith(('.jpg', '.jpeg', '.png'))]

if not arquivos:
    print(f"⚠️ Nenhuma imagem encontrada em '{pasta_entrada}'!")
    exit()

num_variacoes = 5

print(f"📁 Encontradas {len(arquivos)} imagens em '{pasta_entrada}'")
print(f"🔄 Gerando {num_variacoes} variações LEGÍVEIS...\n")

for arquivo in arquivos:
    caminho_arquivo = os.path.join(pasta_entrada, arquivo)
    imagem = cv2.imread(caminho_arquivo)

    if imagem is None:
        print(f"❌ Erro ao carregar: {arquivo}")
        continue
    
    for i in range(num_variacoes):
        if i < 2:
            imagem_aumentada = aumentacoes_quase_original(image=imagem)["image"]
            tipo = "mínima"
        else:
            imagem_aumentada = aumentacoes(image=imagem)["image"]
            tipo = "leve"

        nome_saida = f"aug_{i}_{arquivo}"
        caminho_saida = os.path.join(pasta_saida, nome_saida)
        cv2.imwrite(caminho_saida, imagem_aumentada)
