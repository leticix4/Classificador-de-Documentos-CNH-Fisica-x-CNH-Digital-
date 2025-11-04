import cv2
import csv
import json
import os

# Definir diretório base (onde está o script)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)  # Mudar para o diretório do script

quantidade_imagens = 10
imagem_base = 'cnh_img_base.jpeg'
csv_arquivo = 'dados_fakes.csv'
json_arquivo = 'posicoes.json'
pasta_saida = 'imagens_geradas'

def gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
                  json_arquivo, pasta_saida):
    tamanho_fonte = 0.3
    espessura = 1
    cor_fonte = (0, 0, 0)
    fonte = cv2.FONT_HERSHEY_DUPLEX

    print(f"Trabalhando no diretório: {os.getcwd()}")

    # Verificar arquivos
    for arquivo in [imagem_base, csv_arquivo, json_arquivo]:
        if not os.path.exists(arquivo):
            print(f"ERRO: '{arquivo}' não encontrado em {os.getcwd()}")
            return

    # Ler dados do CSV
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

        # Salvar imagem
        nome_saida = os.path.join(pasta_saida, f'imagem_{id_item}.jpg')
        cv2.imwrite(nome_saida, imagem)
        print(f"✓ Imagem {id_item}/{quantidade_imagens} salva")

    print(f"\n✓ Concluído! {quantidade_imagens} imagens em '{pasta_saida}'")

# Executar
gerar_imagens(quantidade_imagens, imagem_base, csv_arquivo,
              json_arquivo, pasta_saida)