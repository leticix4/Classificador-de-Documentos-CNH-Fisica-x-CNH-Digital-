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

pasta_cnh_digital = r"C:\Users\matos\OneDrive\Área de Trabalho\sistemas_inteligentes_classificador_CNH\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_digital"
pasta_entrada = os.path.join(pasta_cnh_digital, "imagens_geradas")
pasta_saida = os.path.join(pasta_cnh_digital, "imagens_transformadas_legiveis")

os.makedirs(pasta_saida, exist_ok=True)

transformacao = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.RandomRotate90(p=0.5),
    A.MotionBlur(p=0.3),
    A.GaussNoise(p=0.3),
    A.Perspective(p=0.3)
])

arquivos = os.listdir(pasta_entrada)

for arquivo in arquivos:

    caminho_arquivo = os.path.join(pasta_entrada, arquivo)

    imagem = imread_unicode(caminho_arquivo)
    if imagem is None:
        print(f"[ERRO] Não foi possível ler: {caminho_arquivo}")
        continue

    imagem_aumentada = transformacao(image=imagem)["image"]
    caminho_saida = os.path.join(pasta_saida, "aug_" + arquivo)
    imwrite_unicode(caminho_saida, imagem_aumentada)
    print(f"[OK] Salvo: {caminho_saida}")

print("\nProcesso finalizado!")
