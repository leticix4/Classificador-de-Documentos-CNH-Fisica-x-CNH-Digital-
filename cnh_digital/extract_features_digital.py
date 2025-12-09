import cv2
import pytesseract
import os
import numpy as np
import pandas as pd
import colorgram
import argparse
import sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def carregar_imagens(pasta_imagens):
    """Lê todos os arquivos de imagem de uma pasta e retorna seus caminhos."""
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
    """Detecta o primeiro rosto encontrado na imagem e retorna suas coordenadas."""
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        return x, y, w, h
    return None, None, None, None

# cores

def extrair_features(imagem_path):
    """
    Extrai features relacionadas à linha preta da CNH
    """
    # Extrai cores dominantes
    colors = colorgram.extract(imagem_path, 6)
    
    # Lê a imagem com OpenCV
    with open(imagem_path, 'rb') as f:
        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    altura, largura = img.shape[:2]
    
    # Feature 1: Conta pixels pretos (RGB < 50)
    mask_preto = gray < 50
    porcentagem_preto = (np.sum(mask_preto) / (altura * largura)) * 100
    
    # Feature 2: Analisa linha por linha para encontrar linha mais preta
    max_preto_linha = 0
    for i in range(altura):
        pixels_pretos = np.sum(mask_preto[i, :])
        porcentagem_linha = (pixels_pretos / largura) * 100
        if porcentagem_linha > max_preto_linha:
            max_preto_linha = porcentagem_linha
    
    # Feature 3-4: Analisa bordas (superior e inferior)
    borda_sup = int(altura * 0.1)
    borda_inf = int(altura * 0.9)
    
    preto_borda_superior = (np.sum(mask_preto[:borda_sup, :]) / (borda_sup * largura)) * 100
    preto_borda_inferior = (np.sum(mask_preto[borda_inf:, :]) / ((altura - borda_inf) * largura)) * 100
    
    # Feature 5: Conta quantas cores dominantes são pretas
    cores_pretas = 0
    for color in colors:
        if color.rgb.r < 50 and color.rgb.g < 50 and color.rgb.b < 50:
            cores_pretas += 1
    
    # Feature 6-8: RGB médio das 3 primeiras cores dominantes
    cor1_media = (colors[0].rgb.r + colors[0].rgb.g + colors[0].rgb.b) / 3
    cor2_media = (colors[1].rgb.r + colors[1].rgb.g + colors[1].rgb.b) / 3
    cor3_media = (colors[2].rgb.r + colors[2].rgb.g + colors[2].rgb.b) / 3
    
    features = {
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
    
    return features


def processar_dataset(pasta_digital, pasta_fisica, arquivo_saida="features.csv"):
    """
    Processa todas as imagens e salva em CSV
    """
    resultados = []
    
    # Processa CNH Digital
    print("Processando CNH Digital...")
    if os.path.exists(pasta_digital):
        for arquivo in os.listdir(pasta_digital):
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                caminho = os.path.join(pasta_digital, arquivo)
                features = extrair_features(caminho)
                features['classe'] = 'digital'
                resultados.append(features)
                print(f"  ✓ {arquivo}")
    
    # Processa CNH Física
    print("\nProcessando CNH Física...")
    if os.path.exists(pasta_fisica):
        for arquivo in os.listdir(pasta_fisica):
            if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                caminho = os.path.join(pasta_fisica, arquivo)
                features = extrair_features(caminho)
                features['classe'] = 'fisica'
                resultados.append(features)
                print(f"  ✓ {arquivo}")
    
    # Salva em CSV
    if resultados:
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        
        print(f"\n✓ Features salvas em: {arquivo_saida}")
        print(f"Total: {len(resultados)} imagens")

if __name__ == '__main__':
    pasta_digital = "cnh_digital"
    pasta_fisica = "cnh_fisica"
    
    processar_dataset(pasta_digital, pasta_fisica)
# cores

def extrair_texto(img):
    """Extrai texto da imagem usando OCR."""
    return pytesseract.image_to_string(img)


def contar_palavras(texto):
    """Conta o número de palavras em um texto."""
    return len(texto.split())


def processar_imagem(caminho, face_cascade):
    """Processa uma única imagem e retorna um dicionário com os resultados."""
    img = cv2.imread(caminho)
    x, y, w, h = detectar_rosto(img, face_cascade)
    texto = extrair_texto(img)
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
    """Retorna a lista de palavras de interesse para o modelo Bag of Words."""
    return [
        "proibido",
        "plastificar"
    ]

def gerar_features_bag_palavras(df, bag_palavras):
    """Cria colunas de frequência para cada palavra do bag de palavras."""
    for palavra in bag_palavras:
        df[palavra] = df["texto_extraido"].apply(
            lambda texto: texto.lower().split().count(palavra.lower())
        )
    return df


def gerar_csv(resultados, nome_arquivo):
    """Gera um arquivo CSV com os resultados."""
    df = pd.DataFrame(resultados)
    df.to_csv(nome_arquivo, index=False, encoding="utf-8")
    print(f"CSV gerado: {nome_arquivo}")


def main():
    pasta_imagens = Path(r"C:\Users\matos\OneDrive") / "Área de Trabalho" / "sistemas_inteligentes_classificador_CNH" / "Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-" / "cnh_digital" / "imagens_transformadas_legiveis"
    csv_saida = "features_CNH_digital.csv"
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    caminhos_imagens = carregar_imagens(pasta_imagens)
    resultados = []

    for caminho in caminhos_imagens:
        resultado = processar_imagem(caminho, face_cascade)
        resultados.append(resultado)

    df = pd.DataFrame(resultados)

    bag_palavras = obter_bag_palavras()
    df = gerar_features_bag_palavras(df, bag_palavras)

    df.to_csv(csv_saida, index=False, encoding="utf-8")
    print(f"CSV gerado com features: {csv_saida}")


if __name__ == "__main__":
    main()