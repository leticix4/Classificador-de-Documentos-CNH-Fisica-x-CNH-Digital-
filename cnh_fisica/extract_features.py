import cv2
import pytesseract
import os
import pandas as pd
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


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


def extrair_texto(img):
    """Extrai texto da CNH física com pré-processamento para reduzir ruído."""
    
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aumenta contraste
    cinza = cv2.equalizeHist(cinza)

    # Remove ruído do fundo
    blur = cv2.GaussianBlur(cinza, (5, 5), 0)

    # Binarização adaptativa (essencial para CNH antiga)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )

    config = "--oem 3 --psm 6"

    texto = pytesseract.image_to_string(thresh, config=config)

    return texto


def contar_palavras(texto):
    """Conta apenas palavras reais (ignora fragmentos e números soltos)."""
    palavras = re.findall(r'\b[A-Za-zÀ-ÿ]{3,}\b', texto)
    return len(palavras)


def parece_cnh(texto):
    """Heurística simples para detectar se o documento é uma CNH."""
    palavras_chave = ["carteira", "habilitação", "registro", "cpf"]
    count = sum(1 for p in palavras_chave if p in texto.lower())
    return int(count >= 2)


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
        "quantidade_palavras": quantidade_palavras,
        "parece_cnh": parece_cnh(texto)
    }


def obter_bag_palavras():
    """Bag of Words específico para CNH."""
    return [
        "carteira",
        "habilitação",
        "registro",
        "cpf",
        "categoria",
        "validade",
        "emissão",
        "nascimento",
        "brasileiro",
        "filiação"
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
    pasta_imagens = "novas_imagens"
    csv_saida = "features_cnh.csv"
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