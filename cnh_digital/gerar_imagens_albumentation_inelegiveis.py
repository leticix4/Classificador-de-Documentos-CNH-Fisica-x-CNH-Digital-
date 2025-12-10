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
pasta_entrada = r"C:\Users\matos\OneDrive\Documentos\sistemas_inteligentes_classificador_CNH\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_digital\imagens_geradas_digital"
pasta_saida = r"C:\Users\matos\OneDrive\Documentos\sistemas_inteligentes_classificador_CNH\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_digital\imagens_transformadas_inelegiveis"

os.makedirs(pasta_saida, exist_ok=True)

transformacao = A.Compose([
    A.MotionBlur(blur_limit=10, p=0.7),
    A.Defocus(radius=(3, 6), p=0.5),
    A.GaussNoise(var_limit=(50.0, 150.0), p=0.6),
    A.RandomBrightnessContrast(
        brightness_limit=0.35,
        contrast_limit=0.35,
        p=0.7
    ),

    A.PixelDropout(dropout_prob=0.05, p=0.4),
    A.Downscale(scale_min=0.5, scale_max=0.7, p=0.6),
    A.Perspective(scale=(0.05, 0.15), p=0.4),
])


arquivos = os.listdir(pasta_entrada)

for arquivo in arquivos:

    caminho_arquivo = os.path.join(pasta_entrada, arquivo)
    imagem = imread_unicode(caminho_arquivo)

    if imagem is None:
        print(f"[ERRO] Não foi possível ler: {caminho_arquivo}")
        continue

    imagem_inelegivel = transformacao(image=imagem)["image"]
    caminho_saida = os.path.join(pasta_saida, "ineleg_" + arquivo)
    imwrite_unicode(caminho_saida, imagem_inelegivel)
    print(f"[OK] Inelegível salva: {caminho_saida}")
print("\nTransformações concluídas!")
