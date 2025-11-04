import cv2
import albumentations as A
import os
import numpy as np

pasta_entrada = "cnh_digital/imagens_geradas"
pasta_saida = "cnh_digital/imagens_transformadas"
os.makedirs(pasta_entrada, exist_ok=True)
os.makedirs(pasta_saida, exist_ok=True)

aumentacoes = A.Compose([
    A.Resize(256, 256),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.Rotate(limit=15, p=0.5),
    A.GaussNoise(noise_scale_factor=0.5, p=0.3),  
    A.MotionBlur(blur_limit=3, p=0.2),
    A.CLAHE(clip_limit=2, p=0.3),
])


arquivos = [f for f in os.listdir(pasta_entrada) if f.endswith(('.jpg', '.jpeg', '.png'))]

if not arquivos:
    print(f"⚠️ Nenhuma imagem encontrada em '{pasta_entrada}'!")
    print("Por favor, coloque suas imagens nesta pasta e execute novamente.")
    exit()

num_variacoes = 3

print(f"📁 Encontradas {len(arquivos)} imagens em '{pasta_entrada}'")
print(f"🔄 Gerando {num_variacoes} variações de cada imagem...\n")

for arquivo in arquivos:
    caminho_arquivo = os.path.join(pasta_entrada, arquivo)
    imagem = cv2.imread(caminho_arquivo)

    if imagem is None:
        print(f"❌ Erro ao carregar: {arquivo}")
        continue

    print(f"Processando: {arquivo}")
    
    # Aplica aumentações
    for i in range(num_variacoes):
        imagem_aumentada = aumentacoes(image=imagem)["image"]

        nome_saida = f"aug_{i}_{arquivo}"
        caminho_saida = os.path.join(pasta_saida, nome_saida)
        cv2.imwrite(caminho_saida, imagem_aumentada)

        print(f"  ✅ Salva: {nome_saida}")

print(f"\n Processamento concluído! {len(arquivos) * num_variacoes} imagens geradas em '{pasta_saida}'")