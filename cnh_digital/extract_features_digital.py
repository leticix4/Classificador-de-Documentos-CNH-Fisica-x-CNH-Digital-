import cv2
import os
import numpy as np
import pandas as pd
import colorgram
import easyocr
from pathlib import Path

reader = easyocr.Reader(['pt'], gpu=False)


def carregar_imagens(pasta_imagens):
    caminhos = []
    for arquivo in os.listdir(pasta_imagens):
        if arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            caminho = os.path.join(pasta_imagens, arquivo)
            print(f"Lendo imagem {arquivo}")
            
            try:
                with open(caminho, 'rb') as f:
                    file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if img is not None:
                    caminhos.append(caminho)
                    print(f"Carregada")
                else:
                    print(f"Falha ao decodificar")
            except Exception as e:
                print(f"Erro: {e}")
    
    return caminhos


def detectar_rosto(img, face_cascade):
    """Detecta rosto na imagem"""
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        return x, y, w, h
    return None, None, None, None


def extrair_features_cores(imagem_path, img):
    """Extrai features de cores (linha preta)"""
    colors = colorgram.extract(imagem_path, 6)
    
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
        1 for color in colors 
        if color.rgb.r < 50 and color.rgb.g < 50 and color.rgb.b < 50
    )
    
    cor1_media = (colors[0].rgb.r + colors[0].rgb.g + colors[0].rgb.b) / 3
    cor2_media = (colors[1].rgb.r + colors[1].rgb.g + colors[1].rgb.b) / 3
    cor3_media = (colors[2].rgb.r + colors[2].rgb.g + colors[2].rgb.b) / 3
    
    return {
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
    resultado = reader.readtext(img, detail=0)
    return " ".join(resultado)


def contar_palavras(texto):
    return len(texto.split())


def processar_imagem(caminho, face_cascade):
    """Processa uma imagem completa e extrai todas as features"""
    with open(caminho, 'rb') as f:
        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img is None:
        return None
    
    nome_arquivo = os.path.basename(caminho)
    
    x, y, w, h = detectar_rosto(img, face_cascade)
    
    features_cores = extrair_features_cores(caminho, img)
    
    texto = extrair_texto(img)
    quantidade_palavras = contar_palavras(texto)
    
    texto_lower = texto.lower().split()
    freq_proibido = texto_lower.count("proibido")
    freq_plastificar = texto_lower.count("plastificar")
    features = {
        'nome_arquivo': nome_arquivo,
        'x_face': x,
        'y_face': y,
        'w_face': w,
        'h_face': h,
        **features_cores,  
        'texto_extraido': texto.strip(),
        'quantidade_palavras': quantidade_palavras,
        'proibido': freq_proibido,
        'plastificar': freq_plastificar
    }
    
    return features


def main():
    pasta_imagens = Path(
        r"C:\Users\matos\OneDrive\Documentos\sistemas_inteligentes_classificador_CNH"
        r"\Classificador-de-Documentos-CNH-Fisica-x-CNH-Digital-\cnh_digital"
        r"\imagens_transformadas_legiveis"
    )
    
    csv_saida = "features_CNH_digital.csv"
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    print("CARREGANDO IMAGENS")
    caminhos_imagens = carregar_imagens(pasta_imagens)
    
    if not caminhos_imagens:
        print("\nNenhuma imagem encontrada. Verifique o caminho.")
        return
    
    print(f"\n✓ {len(caminhos_imagens)} imagens carregadas")
    print("PROCESSANDO IMAGENS")
    
    resultados = []
    for i, caminho in enumerate(caminhos_imagens, 1):
        print(f"\n[{i}/{len(caminhos_imagens)}] {os.path.basename(caminho)}")
        
        features = processar_imagem(caminho, face_cascade)
        
        if features:
            resultados.append(features)
            print(f"  ✓ Features extraídas com sucesso")
        else:
            print(f"  ✗ Falha ao processar")
    
    if resultados:
        df = pd.DataFrame(resultados)
        df.to_csv(csv_saida, index=False, encoding="utf-8")
        
        print("CSV GERADO COM SUCESSO!")
        print(f"Arquivo: {csv_saida}")
        print(f"Total de imagens processadas: {len(resultados)}")
        print(f"Total de features: {len(df.columns)}")
    else:
        print("\n Nenhuma imagem foi processada com sucesso!")


if __name__ == "__main__":
    main()