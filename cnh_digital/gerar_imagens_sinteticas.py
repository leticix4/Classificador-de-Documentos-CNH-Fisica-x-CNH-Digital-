import cv2
import csv
import json
import os
import glob

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)  

quantidade_imagens = 10
imagem_base = 'cnh_img_base.jpeg'
csv_arquivo = 'dados_fakes.csv'
json_arquivo = 'posicoes.json'
pasta_saida = 'imagens_geradas'
pasta_faces = '../imagens_faces'


def adicionar_biometria_foto(imagem, caminho_face, posicao=(500, 1000), tamanho=(900, 900)):
    """
    Adiciona foto da face na CNH
    
    Args:
        imagem: Imagem da CNH (array numpy)
        caminho_face: Caminho completo da foto da face
        posicao: Tupla (x, y) para posição da foto
        tamanho: Tupla (largura, altura) do tamanho final da foto
    """
    try:
        # Carregar foto da face
        face = cv2.imread(caminho_face)
        
        if face is None:
            print(f"ERRO: Não foi possível ler: {caminho_face}")
            return imagem
        
        print(f"Face carregada: {face.shape}")
        
        # Redimensiona para o tamanho desejado
        face_resized = cv2.resize(face, tamanho, interpolation=cv2.INTER_AREA)
        print(f"✓ Face redimensionada para: {face_resized.shape}")
        x, y = posicao
        h, w = face_resized.shape[:2]
        
        # Verificar se cabe na imagem
        if y + h > imagem.shape[0] or x + w > imagem.shape[1]:
            print(f"AVISO: Foto não cabe na posição ({x}, {y})")
            print(f"CNH: {imagem.shape[1]}x{imagem.shape[0]}")
            print(f"Foto: {w}x{h}")
            print(f"Fim da foto: ({x+w}, {y+h})")
            return imagem
        
        # Sobrepor a foto na CNH
        imagem[y:y+h, x:x+w] = face_resized
        print(f"Foto adicionada com sucesso em ({x}, {y})")
        
        return imagem
        
    except Exception as e:
        print(f"ERRO na função adicionar_biometria_foto: {e}")
        import traceback
        traceback.print_exc()
        return imagem


def gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
                  json_arquivo, pasta_saida):
    tamanho_fonte = 0.5
    espessura = 1
    cor_fonte = (0, 0, 0)
    fonte = cv2.FONT_HERSHEY_DUPLEX

    print("="*70)
    print("INICIANDO GERADOR DE CNH COM FOTOS")
    print("="*70)
    print(f"\nDiretório de trabalho: {os.getcwd()}\n")
    print("Verificando arquivos necessários...")
    for arquivo in [imagem_base, csv_arquivo, json_arquivo]:
        existe = os.path.exists(arquivo)
        if not existe:
            print(f"Caminho completo: {os.path.abspath(arquivo)}")
            return

    # Verificar pasta de faces
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

    # cria pasta de saída
    os.makedirs(pasta_saida, exist_ok=True)
    print(f"\n📂 Pasta de saída: {os.path.abspath(pasta_saida)}")

    quantidade_imagens = min(quantidade_imagens, len(dados_csv))

    # campos preenchidos
    campos = [
        "nome_completo", "prim_habi", "data_nasci", "local_nasci", "uf_3",
        "data_emissao", "validade", "doc_identida", "org_emissor",
        "uf_4c", "cpf", "num_regis", "categoria", "pai", "mae", "assinatura"
    ]
    extensoes = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
    imagens_faces = []
    for ext in extensoes:
        imagens_faces.extend(glob.glob(os.path.join(pasta_faces, ext)))
    
    if not imagens_faces:
        print(f"NENHUMA imagem encontrada em '{pasta_faces}'")
        print(f"Caminho completo: {os.path.abspath(pasta_faces)}")
        print(f"Extensões buscadas: {extensoes}")
        return

    print(f"✓ {len(imagens_faces)} imagens encontradas:")
    for i, img in enumerate(imagens_faces[:5], 1): 
        print(f"   {i}. {os.path.basename(img)}")
    if len(imagens_faces) > 5:
        print(f"   ... e mais {len(imagens_faces) - 5}")

    # Gerar imagens
    print(f"\n{'='*70}")
    print(f"GERANDO {quantidade_imagens} IMAGENS")
    print(f"{'='*70}\n")

    for id_item, dado in enumerate(dados_csv[:quantidade_imagens], start=1):
        print(f"\n--- Imagem {id_item}/{quantidade_imagens} ---")
        
        # carrega imagem base
        imagem = cv2.imread(imagem_base)
        
        if imagem is None:
            print(f"ERRO: Não foi possível carregar '{imagem_base}'")
            return
        
        print(f"✓ CNH base carregada: {imagem.shape[1]}x{imagem.shape[0]} pixels")

        # add textos
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
        
        # mod de tamanho e posicao da biometria
        posicao_foto = (215, 295)  
        tamanho_foto = (290, 380)  
        
        imagem = adicionar_biometria_foto(imagem, caminho_face, posicao_foto, tamanho_foto)
        nome_saida = os.path.join(pasta_saida, f'cnh_{id_item:03d}.jpg')
        sucesso = cv2.imwrite(nome_saida, imagem)
        
        if sucesso:
            print(f"Salva: {nome_saida}")
        else:
            print(f"ERRO ao salvar: {nome_saida}")

    print(f"\n{'='*70}")
    print(f"CONCLUÍDO! {quantidade_imagens} imagens geradas")
    print(f"{'='*70}")


# Executar
try:
    gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
                  json_arquivo, pasta_saida)
except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()