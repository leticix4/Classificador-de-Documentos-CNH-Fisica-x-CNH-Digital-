import csv
import random
from faker import Faker

def gerar_csv(qtd_itens, nome_arquivo="dados_fakes.csv"):
    fake = Faker('pt_BR')
    categoria_hab = ["A", "B", "C", "D", "E"]

    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["nome_completo", "prim_habi", "data_local_uf", "data_emissao", "validade", "doc_identida_org_emissor_uf", "cpf", "num_regis", "categoria", "filiacao", "assinatura"])
        for _ in range(qtd_itens):
            nome = fake.name()
            tipo = random.choice(categoria_hab)
            escritor.writerow([nome, tipo])

    print(f"{qtd_itens} registros salvos em '{nome_arquivo}'")

if __name__ == "__main__":
    qtd = int(input("Quantos registros deseja gerar? "))
    gerar_csv(qtd)