import cv2
import csv
import json
import os
import glob

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)  

quantidade_imagens = 100
imagem_base = 'CNHFisica.jpg'
csv_arquivo = 'dados_fakes.csv'
json_arquivo = 'posicoes.json'
pasta_saida = 'imagens_geradas'
pasta_faces = '../imagens_faces'
pasta_assinaturas = 'assinaturas'  # pasta opcional com imagens de assinatura (PNG com alpha recomendado)


def adicionar_biometria_foto(imagem, caminho_face, posicao=(395, 552), tamanho=(900, 900)):
    """
    Adiciona foto da face na CNH
    """
    try:
        face = cv2.imread(caminho_face)
        if face is None:
            print(f"ERRO: Não foi possível ler: {caminho_face}")
            return imagem
        face_resized = cv2.resize(face, tamanho, interpolation=cv2.INTER_AREA)
        x, y = posicao
        h, w = face_resized.shape[:2]
        if y + h > imagem.shape[0] or x + w > imagem.shape[1]:
            print(f"AVISO: Foto não cabe na posição ({x}, {y}) — pulando")
            return imagem
        imagem[y:y+h, x:x+w] = face_resized
        return imagem
    except Exception as e:
        print(f"ERRO na função adicionar_biometria_foto: {e}")
        import traceback; traceback.print_exc()
        return imagem


def adicionar_assinatura(imagem, assinatura_valor, posicao=(600, 1400), tamanho=(350, 120), alpha=0.9):
    """
    Insere assinatura digital na imagem.
    - assinatura_valor: pode ser
        * caminho para arquivo de imagem (PNG/JPG) -> será sobreposto com blend (respeita alpha de PNG)
        * texto -> será desenhado como assinatura sintética usando fonte script do OpenCV
    - posicao: (x, y) do canto superior esquerdo onde a assinatura será colocada
    - tamanho: (largura, altura) desejada para a assinatura (para imagens)
    - alpha: opacidade (0.0 a 1.0) para blending (quando for imagem sem alpha)
    Retorna a imagem alterada.
    """
    try:
        x, y = posicao
        max_w, max_h = tamanho

        # Se valor é caminho válido pra imagem
        if isinstance(assinatura_valor, str) and os.path.exists(assinatura_valor):
            sig = cv2.imread(assinatura_valor, cv2.IMREAD_UNCHANGED)  # mantém canal alpha se houver
            if sig is None:
                print(f"AVISO: assinatura em '{assinatura_valor}' não pôde ser lida. Usando texto.")
            else:
                # redimensionar mantendo canais
                sig_h, sig_w = sig.shape[:2]
                scale_w = max_w / sig_w
                scale_h = max_h / sig_h
                scale = min(scale_w, scale_h, 1.0)
                new_w = int(sig_w * scale)
                new_h = int(sig_h * scale)
                sig_resized = cv2.resize(sig, (new_w, new_h), interpolation=cv2.INTER_AREA)

                # verifica espaço
                if y + new_h > imagem.shape[0] or x + new_w > imagem.shape[1]:
                    print("AVISO: assinatura (imagem) não cabe na posição especificada — ajustando posição para caber.")
                    # ajusta para caber na borda direita/baixa
                    x = min(x, imagem.shape[1] - new_w)
                    y = min(y, imagem.shape[0] - new_h)

                # Se imagem tem alpha (4 canais) -> uso alpha para blending
                if sig_resized.shape[2] == 4:
                    alpha_channel = sig_resized[:, :, 3] / 255.0
                    rgb_sig = sig_resized[:, :, :3]
                    h, w = rgb_sig.shape[:2]

                    roi = imagem[y:y+h, x:x+w].astype(float)
                    fg = rgb_sig.astype(float)

                    # blend por pixel
                    for c in range(3):
                        roi[:, :, c] = (alpha_channel * fg[:, :, c] + (1 - alpha_channel) * roi[:, :, c])

                    imagem[y:y+h, x:x+w] = roi.astype('uint8')
                    return imagem
                else:
                    # sem alpha -> aplicar blend com alpha uniform
                    h, w = sig_resized.shape[:2]
                    if y + h > imagem.shape[0] or x + w > imagem.shape[1]:
                        print("AVISO: assinatura (imagem sem alpha) não cabe completamente — pulando.")
                        return imagem
                    roi = imagem[y:y+h, x:x+w].astype(float)
                    fg = sig_resized.astype(float)
                    blended = cv2.addWeighted(fg, alpha, roi, 1 - alpha, 0)
                    imagem[y:y+h, x:x+w] = blended.astype('uint8')
                    return imagem

        # Se não é caminho válido: desenhar texto como assinatura sintética
        texto = str(assinatura_valor) if assinatura_valor is not None else "Assinatura Fictícia"
        # tenta fonte "script" para assemelhar caligrafia
        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        # estima tamanho da fonte para caber na largura desejada
        # encontra maior fontScale que caiba na largura max_w
        font_scale = 0.8
        thickness = 1
        (tw, th), _ = cv2.getTextSize(texto, font, font_scale, thickness)
        # ajusta scale baseado em largura e altura
        if tw > 0:
            scale_w = max_w / tw
        else:
            scale_w = 1.0
        if th > 0:
            scale_h = max_h / th
        else:
            scale_h = 1.0
        font_scale = min(scale_w, scale_h, 2.5)
        thickness = max(1, int(font_scale * 2))

        # verifica se cabe; se não couber, move para dentro da imagem
        (tw, th), _ = cv2.getTextSize(texto, font, font_scale, thickness)
        if y + th > imagem.shape[0]:
            y = imagem.shape[0] - th - 5
        if x + tw > imagem.shape[1]:
            x = imagem.shape[1] - tw - 5
        # desenha com leve sombra para realismo
        cv2.putText(imagem, texto, (x+1, y+1+th), font, font_scale, (180,180,180), thickness, cv2.LINE_AA)
        cv2.putText(imagem, texto, (x, y+th), font, font_scale, (0,0,0), thickness, cv2.LINE_AA)
        return imagem

    except Exception as e:
        print(f"ERRO na função adicionar_assinatura: {e}")
        import traceback; traceback.print_exc()
        return imagem


def gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
                  json_arquivo, pasta_saida):
    tamanho_fonte = 0.5
    espessura = 1
    cor_fonte = (0, 0, 0)
    fonte = cv2.FONT_HERSHEY_DUPLEX

    print("="*70)
    print("INICIANDO GERADOR DE CNH COM FOTOS E ASSINATURAS")
    print("="*70)
    print(f"\nDiretório de trabalho: {os.getcwd()}\n")
    print("Verificando arquivos necessários...")
    for arquivo in [imagem_base, csv_arquivo, json_arquivo]:
        existe = os.path.exists(arquivo)
        if not existe:
            print(f"Caminho completo: {os.path.abspath(arquivo)}")
            return

    existe_pasta = os.path.exists(pasta_faces)
    if not existe_pasta:
        print(f"Caminho completo: {os.path.abspath(pasta_faces)}")
        return
    dados_csv = []
    with open(csv_arquivo, newline='', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            dados_csv.append(linha)
    print(f" {len(dados_csv)} registros carregados")
    with open(json_arquivo, 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
    print(f"✓ {len(dados_json)} posições carregadas")

    os.makedirs(pasta_saida, exist_ok=True)
    print(f"\n Pasta de saída: {os.path.abspath(pasta_saida)}")

    quantidade_imagens = min(quantidade_imagens, len(dados_csv))

    campos = [
        "nome_completo", "prim_habi", "data_nasci", "local_nasci", "uf_3",
        "data_emissao", "validade", "doc_identida", "org_emissor",
        "uf_4c", "cpf", "num_regis", "categoria", "pai", "mae"
    ]
    extensoes = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
    imagens_faces = []
    for ext in extensoes:
        imagens_faces.extend(glob.glob(os.path.join(pasta_faces, ext)))
    
    if not imagens_faces:
        print(f"NENHUMA imagem encontrada em '{pasta_faces}'")
        return

    imagens_assin = []
    for ext in extensoes:
        imagens_assin.extend(glob.glob(os.path.join(pasta_assinaturas, ext)))
    if imagens_assin:
        print(f"✓ {len(imagens_assin)} imagens de assinatura encontradas (usar se CSV não apontar arquivo específico).")

    print(f"\n{'='*70}")
    print(f"GERANDO {quantidade_imagens} IMAGENS")
    print(f"{'='*70}\n")

    for id_item, dado in enumerate(dados_csv[:quantidade_imagens], start=1):
        print(f"\n--- Imagem {id_item}/{quantidade_imagens} ---")
        imagem = cv2.imread(imagem_base)
        if imagem is None:
            print(f"ERRO: Não foi possível carregar '{imagem_base}'")
            return
        print(f"✓ CNH base carregada: {imagem.shape[1]}x{imagem.shape[0]} pixels")

        # add textos (campos encontrados)
        for campo in campos:
            if campo in dado and campo in dados_json:
                texto = str(dado[campo])
                posicao = tuple(dados_json[campo])
                cv2.putText(imagem, texto, posicao, fonte, 
                           tamanho_fonte, cor_fonte, espessura, cv2.LINE_AA)

        # add biometria
        idx_face = (id_item - 1) % len(imagens_faces)
        caminho_face = imagens_faces[idx_face]
        print(f"Adicionando foto: {os.path.basename(caminho_face)}")
        posicao_foto = (215+40, 295+82)  
        tamanho_foto = (290, 380)  
        imagem = adicionar_biometria_foto(imagem, caminho_face, posicao_foto, tamanho_foto)

        # Prioridade para um caminho especificado no CSV (campo 'assinatura'):
        assinatura_valor = None
        if 'assinatura' in dado and dado['assinatura'].strip():
            possivel = dado['assinatura'].strip()
            # se for caminho relativo/existente, usa-o; senão tratar como texto
            if os.path.exists(possivel):
                assinatura_valor = possivel
            else:
                # tenta em pasta_assinaturas com nome indicado
                possivel2 = os.path.join(pasta_assinaturas, possivel)
                if os.path.exists(possivel2):
                    assinatura_valor = possivel2
                else:
                    # se não existir como arquivo, trate como texto (nome ou token)
                    assinatura_valor = possivel

        # se CSV não definiu assinatura e houver imagens em pasta_assinaturas, use uma com base no índice
        if assinatura_valor is None and imagens_assin:
            assinatura_valor = imagens_assin[(id_item - 1) % len(imagens_assin)]

        # definir posição da assinatura: tenta usar chave 'pos_assinatura' no json; senão usa default
        if 'pos_assinatura' in dados_json:
            pos_ass = tuple(dados_json['pos_assinatura'])
        elif 'assinatura' in dados_json:
            pos_ass = tuple(dados_json['assinatura'])
        else:
            pos_ass = (600, 1400)

        tamanho_assin = (180, 80)  # ajuste se precisar
        print(f"Adicionando assinatura (valor: {assinatura_valor}) em {pos_ass}")
        imagem = adicionar_assinatura(imagem, assinatura_valor, posicao=pos_ass, tamanho=tamanho_assin, alpha=0.9)

        nome_saida = os.path.join(pasta_saida, f'cnh_{id_item:03d}.jpg')
        sucesso = cv2.imwrite(nome_saida, imagem)
        if sucesso:
            print(f"Salva: {nome_saida}")
        else:
            print(f"ERRO ao salvar: {nome_saida}")

    print(f"\n{'='*70}")
    print(f"CONCLUÍDO! {quantidade_imagens} imagens geradas")
    print(f"{'='*70}")
try:
    gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
                  json_arquivo, pasta_saida)
except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()
