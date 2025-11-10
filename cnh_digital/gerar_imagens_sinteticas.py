import cv2
import csv
import json
import os
import glob


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)  

quantidade_imagens = 10
imagem_base = 'cnh_img_base.jpeg'
csv_arquivo = '../dados_fakes.csv'
json_arquivo = 'posicoes.json'
pasta_saida = '../imagens_geradas'
pasta_faces = '../imagens_faces'  


def adicionar_biometria_foto(imagem, imagem_face, posicao=(204, 405), escala=0.3):
    biometria = cv2.imread(imagem_face, cv2.IMREAD_UNCHANGED)
    if biometria is None:
        print(f"❌ Imagem de biometria '{imagem_face}' não encontrada.")
        return imagem

    largura = int(biometria.shape[1] * escala)
    altura = int(biometria.shape[0] * escala)
    biometria = cv2.resize(biometria, (largura, altura), interpolation=cv2.INTER_AREA)

    x, y = posicao
    y1, y2 = y, y + biometria.shape[0]
    x1, x2 = x, x + biometria.shape[1]

    if x2 > imagem.shape[1] or y2 > imagem.shape[0]:
        print("⚠️ Foto fora dos limites da CNH.")
        return imagem

    if biometria.shape[2] == 4:
        alpha = biometria[:, :, 3] / 255.0
        alpha = alpha[..., None]
        biometria_rgb = biometria[:, :, :3].astype(float)
        imagem[y1:y2, x1:x2] = (
            alpha * biometria_rgb + (1 - alpha) * imagem[y1:y2, x1:x2].astype(float)
        ).astype('uint8')
    else:
        imagem[y1:y2, x1:x2] = biometria

    print(f"✅ Foto '{imagem_face}' adicionada em {posicao}")
    return imagem


def gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
                  json_arquivo, pasta_saida):
    tamanho_fonte = 0.3
    espessura = 1
    cor_fonte = (0, 0, 0)
    fonte = cv2.FONT_HERSHEY_DUPLEX

    print(f"Trabalhando no diretório: {os.getcwd()}")

    for arquivo in [imagem_base, csv_arquivo, json_arquivo]:
        if not os.path.exists(arquivo):
            print(f"ERRO: '{arquivo}' não encontrado em {os.getcwd()}")
            return

    if not os.path.exists(pasta_faces):
        print(f"ERRO: Pasta '{pasta_faces}' não encontrada em {os.getcwd()}")
        return
    
    dados_csv = []
    with open(csv_arquivo, newline='', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            dados_csv.append(linha)

    print(f"{len(dados_csv)} registros carregados do CSV")

    # Ler posições do JSON
    with open(json_arquivo, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
        print(f"Posições carregadas: {list(dados_json.keys())}")

    # Criar pasta de saída
    os.makedirs(pasta_saida, exist_ok=True)

    quantidade_imagens = min(quantidade_imagens, len(dados_csv))

    # Campos a serem preenchidos
    campos = [
        "nome_completo", "prim_habi", "data_nasci", "local_nasci", "uf_3",
        "data_emissao", "validade", "doc_identida", "org_emissor",
        "uf_4c", "cpf", "num_regis", "categoria", "pai", "mae", "assinatura"
    ]

    # Obter lista de imagens de faces disponíveis
    imagens_faces = glob.glob(os.path.join(pasta_faces, "*.jpg")) + \
                   glob.glob(os.path.join(pasta_faces, "*.jpeg")) + \
                   glob.glob(os.path.join(pasta_faces, "*.png"))
    
    if not imagens_faces:
        print(f"❌ Nenhuma imagem encontrada na pasta '{pasta_faces}'")
        return

    print(f"📸 {len(imagens_faces)} imagens de biometria encontradas")

    # Gerar imagens
    for id_item, dado in enumerate(dados_csv[:quantidade_imagens], start=1):
        imagem = cv2.imread(imagem_base)
        
        if imagem is None:
            print(f"ERRO: Não foi possível carregar '{imagem_base}'")
            return

        # Adicionar cada campo na imagem
        for campo in campos:
            if campo in dado and campo in dados_json:
                texto = str(dado[campo])
                posicao = tuple(dados_json[campo])
                cv2.putText(imagem, texto, posicao, fonte, 
                           tamanho_fonte, cor_fonte, espessura, cv2.LINE_AA)

        # ADIÇÃO: Adicionar biometria/foto da pessoa
        # Usar imagem de face correspondente ao índice (cíclico se houver menos faces que imagens)
        imagem_face = imagens_faces[(id_item - 1) % len(imagens_faces)]
        
        # Posição da foto na CNH (ajuste conforme necessário)
        posicao_foto = (204, 405)  # Exemplo - ajuste para sua CNH
        
        imagem = adicionar_biometria_foto(imagem, imagem_face, posicao_foto)
 
        # Salvar imagem
        nome_saida = os.path.join(pasta_saida, f'imagem_{id_item}.jpg')
        cv2.imwrite(nome_saida, imagem)
        print(f"✓ Imagem {id_item}/{quantidade_imagens} salva")

    print(f"\n✓ Concluído! {quantidade_imagens} imagens em '{pasta_saida}'")


gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
              json_arquivo, pasta_saida)