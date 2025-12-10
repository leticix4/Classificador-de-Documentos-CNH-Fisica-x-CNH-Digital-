import cv2
import albumentations as A
import os
import numpy as np

def imread_unicode(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)

def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    encoded = cv2.imencode(ext, img)[1]
    encoded.tofile(path)


pasta_entrada = r"C:\Users\letic\OneDrive\Documentos\SI\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_fisica\imagens_geradas"
pasta_saida = r"C:\Users\letic\OneDrive\Documentos\SI\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_fisica\imagens_transformadas_inelegiveis"

os.makedirs(pasta_saida, exist_ok=True)


transformacao = A.Compose([
    A.MotionBlur(blur_limit=11, p=0.7),
    A.Defocus(radius=(3, 6), p=0.5),
    A.GaussNoise(std_range=(0.2, 0.5), p=0.6),

    A.RandomBrightnessContrast(
        brightness_limit=0.35,
        contrast_limit=0.35,
        p=0.7
    ),

    A.PixelDropout(dropout_prob=0.05, p=0.4),
    A.Downscale(scale_range=(0.5, 0.7), p=0.6),
    A.Perspective(scale=(0.05, 0.15), p=0.4),
])


if not os.path.exists(pasta_entrada):
    print(" ERRO: Pasta não encontrada:", pasta_entrada)
    exit()

arquivos = os.listdir(pasta_entrada)

for arquivo in arquivos:

    caminho_arquivo = os.path.join(pasta_entrada, arquivo)

    if not os.path.isfile(caminho_arquivo):
        continue

    if not arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
        continue

    imagem = imread_unicode(caminho_arquivo)


    if imagem is None:
        print(f"[ERRO] Não foi possível ler: {caminho_arquivo}")
        continue

    imagem_inelegivel = transformacao(image=imagem)["image"]
    caminho_saida = os.path.join(pasta_saida, "ineleg_" + arquivo)
    imwrite_unicode(caminho_saida, imagem_inelegivel)

    print(f"[OK] Inelegível salva: {caminho_saida}")

print("\n Transformações concluídas com sucesso!")
