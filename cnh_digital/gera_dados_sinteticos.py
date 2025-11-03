import csv
import random
from faker import Faker
from faker.providers import person, ssn
import unicodedata

def remover_acentos(texto: str) -> str:
    """
    Remove acentos e cedilhas de qualquer string.
    """
    if not isinstance(texto, str):
        return texto
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def gerar_csv(qtd_itens, nome_arquivo="dados_fakes.csv"):
    fake = Faker('pt_BR')
    categoria_hab = ["A", "B", "C", "D", "E"]

    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["nome_completo", "prim_habi", "data_nasci", "local_nasci", "uf_3", "data_emissao", 
            "validade", "doc_identida", "org_emissor", "uf_4c", "cpf", "num_regis", "categoria", "pai", "mae", "assinatura"])
        for _ in range(qtd_itens):
            nome = fake.name()
            nome_sem_acentos = remover_acentos(nome)
            tipo = random.choice(categoria_hab)
            cpf = fake.cpf()

            escritor.writerow([nome_sem_acentos, tipo, "", "", "", "","", "", "", "", cpf, "", "", "", "", "" ])

    print(f"{qtd_itens} registros salvos em '{nome_arquivo}'")

if __name__ == "__main__":
    qtd = int(input("Quantos registros deseja gerar? "))
    gerar_csv(qtd)