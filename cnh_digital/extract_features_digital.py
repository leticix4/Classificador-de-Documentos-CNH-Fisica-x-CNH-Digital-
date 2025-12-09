import cv2
import os
import numpy as np
import pandas as pd
import colorgram
import csv
import easyocr
from pathlib import Path

reader = easyocr.Reader(['pt'])  # carrega OCR em português

def carregar_imagens(pasta_imagens):
    caminhos = []
    for arquivo in os.listdir(pasta_imagens):
        print(f"Lendo imagem {arquivo}")
        caminho = os.path.join(pasta_imagens, arquivo)
        if cv2.imread(caminho) is not None:
            caminhos.append(caminho)
        else:
            print(f"Arquivo {arquivo} não é uma imagem válida, pulando")
    return caminhos


def detectar_rosto(img, face_cascade):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        return x, y, w, h
    return None, None, None, None


def extrair_features(imagem_path):
    colors = colorgram.extract(imagem_path, 6)
    
    with open(imagem_path, 'rb') as f:
        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    altura, largura = img.shape[:2]
    
    mask_preto = gray < 50
    porcentagem_preto = (np.sum(mask_preto) / (altura * largura)) * 100
    
    max_preto_linha = 0
    for i in range(altura):
        pixels_pretos = np.sum(mask_preto[i, :])
        porcentagem_linha = (pixels_pretos / largura) * 100
        if porcentagem_linha > max_preto_linha:
            max_preto_linha = porcentagem_linha
    
    borda_sup = int(altura * 0.1)
    borda_inf = int(altura * 0.9)
    
    preto_borda_superior = (np.sum(mask_preto[:borda_sup, :]) / (borda_sup * largura)) * 100
    preto_borda_inferior = (np.sum(mask_preto[borda_inf:, :]) / ((altura - borda_inf) * largura)) * 100
    
    cores_pretas = sum(
        1 for color in colors if color.rgb.r < 50 and color.rgb.g < 50 and color.rgb.b < 50
    )

    cor1_media = (colors[0].rgb.r + colors[0].rgb.g + colors[0].rgb.b) / 3
    cor2_media = (colors[1].rgb.r + colors[1].rgb.g + colors[1].rgb.b) / 3
    cor3_media = (colors[2].rgb.r + colors[2].rgb.g + colors[2].rgb.b) / 3
    
    return {
        'arquivo': os.path.basename(imagem_path),
        'porcentagem_preto': round(porcentagem_preto, 2),
        'max_preto_linha': round(max_preto_linha, 2),
        'preto_borda_superior': round(preto_borda_superior, 2),
        'preto_borda_inferior': round(preto_borda_inferior, 2),
        'cores_pretas': cores_pretas,
        'cor1_media': round(cor1_media, 2),
        'cor2_media': round(cor2_media, 2),
        'cor3_media': round(cor3_media, 2)
    }


def extrair_texto(img):
    """OCR usando EasyOCR (sem Tesseract)."""
    resultado = reader.readtext(img, detail=0)
    return " ".join(resultado)

def contar_palavras(texto):
    return len(texto.split())

def processar_imagem(caminho, face_cascade):
    img = cv2.imread(caminho)
    x, y, w, h = detectar_rosto(img, face_cascade)
    texto = extrair_texto(caminho)  # EasyOCR aceita path OU imagem
    quantidade_palavras = contar_palavras(texto)

    return {
        "nome_arquivo": os.path.basename(caminho),
        "x_face": x,
        "y_face": y,
        "w_face": w,
        "h_face": h,
        "texto_extraido": texto.strip(),
        "quantidade_palavras": quantidade_palavras
    }

def obter_bag_palavras():
    return ["proibido", "plastificar"]

def gerar_features_bag_palavras(df, bag_palavras):
    for palavra in bag_palavras:
        df[palavra] = df["texto_extraido"].apply(
            lambda texto: texto.lower().split().count(palavra.lower())
        )
    return df


def main():

    pasta_imagens = Path(
        r"C:\Users\matos\OneDrive\Documentos\sistemas_inteligentes_classificador_CNH\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_digital\imagens_transformadas_legiveis"
    )

    csv_saida = "features_CNH_digital.csv"
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    caminhos_imagens = carregar_imagens(pasta_imagens)

    if not caminhos_imagens:
        print("Nenhuma imagem encontrada. Verifique o caminho.")
        return

    resultados = [processar_imagem(c, face_cascade) for c in caminhos_imagens]

    df = pd.DataFrame(resultados)

    bag_palavras = obter_bag_palavras()
    df = gerar_features_bag_palavras(df, bag_palavras)

    df.to_csv(csv_saida, index=False, encoding="utf-8")
    print(f"CSV gerado com features: {csv_saida}")

if __name__ == "__main__":
    main()
