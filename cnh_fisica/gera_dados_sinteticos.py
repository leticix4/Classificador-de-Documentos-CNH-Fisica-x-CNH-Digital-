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

""" funçao de gerar dados """
def gerar_csv(qtd_itens, nome_arquivo="dados_fakes.csv"):
    fake = Faker('pt_BR')
    fake.add_provider(person)
    fake.add_provider(ssn)
    categoria_hab = ["A", "B", "C", "D", "E"]

    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["nome_completo", "prim_habi", "data_local_uf", "data_emissao", "validade", "doc_identida_org_emissor_uf", "cpf", "num_regis", "categoria", "filiacao", "assinatura"])
        for _ in range(qtd_itens):
            nome =fake.name()
            nome_sem_acentos = remover_acentos(nome)
            tipo = random.choice(categoria_hab)
            cpf = fake.cpf()

            escritor.writerow([nome_sem_acentos, tipo, "", "", "", "", cpf, "", "", "", ""])

    print(f"{qtd_itens} registros salvos em '{nome_arquivo}'")

if __name__ == "__main__":
    qtd = int(input("Quantos registros deseja gerar? "))
    gerar_csv(qtd)