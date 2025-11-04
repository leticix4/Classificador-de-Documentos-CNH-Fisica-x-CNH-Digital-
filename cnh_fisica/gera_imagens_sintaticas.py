import cv2
import csv
import json
import os
import sys

quantidade_imagens= 6
imagem_base = 'CNHFisica.jpg'
csv_arquivo = 'dados_fakes.csv'
json_arquivo = 'posicoes.json'

pasta_saida =''

def gerar_imagens (quantidade_imagens, imagem_base, csv_arquivo,
                   json_arquivo, pasta_saida):
  tamanho_fonte = 0.7
  cor_fonte= (0, 0, 0)
  fonte =cv2.FONT_HERSHEY_DUPLEX


  dados_csv = []

  with open(csv_arquivo, newline= '',encoding='utf-8') as f:
    leitor = csv.DictReader(f)
    for linha in leitor:
      dados_csv.append(linha)
      print(linha)

  with open(json_arquivo, 'r')as f:
    dados_json = json.load(f)
    print (dados_json)

  quantidade_imagens= min(quantidade_imagens, len(dados_csv))
  os.makedirs('/content/imagem_geradas', exist_ok=True)

  for id_item, dado in enumerate(dados_csv[:quantidade_imagens], start = 1):
    imagem=cv2.imread(imagem_base)
    print(dado)
    cv2.putText(imagem, dado['nome_completo'], tuple (dados_json['nome_completo']),
                fonte, tamanho_fonte, cor_fonte, 1, cv2.LINE_AA)
    

    cv2.putText(imagem, dado['prim_habi'], tuple (dados_json['prim_habi']),
                fonte, tamanho_fonte , cor_fonte, 1, cv2.LINE_AA)
    
    cv2.putText(imagem, dado['data_nasci'], tuple (dados_json['data_nasci']),
                fonte, tamanho_fonte, cor_fonte, 1, cv2.LINE_AA)
    
    cv2.putText(imagem, dado['local_nasci'], tuple (dados_json['local_nasci']),
                fonte, tamanho_fonte, cor_fonte, 1, cv2.LINE_AA)
    
    cv2.putText(imagem, dado['uf_3'], tuple (dados_json['uf_3']),
                fonte, tamanho_fonte, cor_fonte, 1, cv2.LINE_AA)
    
    cv2.putText(imagem, dado['data_emissao'], tuple (dados_json['data_emissao']),
                fonte, tamanho_fonte, cor_fonte, 1, cv2.LINE_AA)

    cv2.putText(imagem, dado['validade'], tuple (dados_json['validade']),
                fonte, tamanho_fonte, cor_fonte, 1, cv2.LINE_AA)

    nome_saida = os.path.join(pasta_saida, f'imagem_{id_item}.jpg')
    cv2.imwrite(nome_saida, imagem)

        
gerar_imagens (quantidade_imagens, imagem_base, csv_arquivo,
                   json_arquivo, pasta_saida)

