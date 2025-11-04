import csv
import random
from faker import Faker
from faker.providers import person, ssn
import unicodedata
from datetime import datetime, timedelta

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

def gerar_numero_registro_cnh():
    """
    Gera um número de registro de CNH (11 dígitos).
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def gerar_rg():
    """
    Gera um número de RG no formato XX.XXX.XXX-X.
    """
    return f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"

def gerar_orgao_emissor():
    """
    Gera um órgão emissor de RG comum no Brasil.
    """
    orgaos = ["SSP", "DETRAN", "PC", "IFP", "IIRGD", "IPF"]
    return random.choice(orgaos)

def gerar_csv(qtd_itens, nome_arquivo="dados_fakes.csv"):
    fake = Faker('pt_BR')
    categoria_hab = ["A", "B", "C", "D", "E"]
    estados_br = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                  "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
                  "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["nome_completo", "prim_habi", "data_nasci", "local_nasci", "uf_3", "data_emissao", 
            "validade", "doc_identida", "org_emissor", "uf_4c", "cpf", "num_regis", "categoria", "pai", "mae", "assinatura"])
        
        for _ in range(qtd_itens):
            
            nome = fake.name()
            nome_sem_acentos = remover_acentos(nome)
            tipo = random.choice(categoria_hab)
            cpf = fake.cpf()
            
            # Data de nascimento (entre 18 e 80 anos atrás)
            data_nascimento = fake.date_of_birth(minimum_age=18, maximum_age=80)
            data_nasci_formatada = data_nascimento.strftime("%d/%m/%Y")                      
            local_nascimento = remover_acentos(fake.city())
            uf_nascimento = random.choice(estados_br)
            
            # Data de emissão (entre 1 e 10 anos atrás)
            data_emissao = fake.date_between(start_date='-10y', end_date='-1y')
            data_emissao_formatada = data_emissao.strftime("%d/%m/%Y")
            validade = data_emissao + timedelta(days=365*10)
            validade_formatada = validade.strftime("%d/%m/%Y")
            rg = gerar_rg()
            orgao_emissor = gerar_orgao_emissor()
            uf_rg = random.choice(estados_br)
            num_registro = gerar_numero_registro_cnh()
            nome_pai = fake.name_male()
            nome_pai_sem_acentos = remover_acentos(nome_pai)
            nome_mae = fake.name_female()
            nome_mae_sem_acentos = remover_acentos(nome_mae)
            
            # Assinatura (mesmo que o nome completo)
            assinatura = nome_sem_acentos

            escritor.writerow([
                nome_sem_acentos,           # nome_completo
                tipo,                        # prim_habi
                data_nasci_formatada,       # data_nasci
                local_nascimento,           # local_nasci
                uf_nascimento,              # uf_3
                data_emissao_formatada,     # data_emissao
                validade_formatada,         # validade
                rg,                         # doc_identida
                orgao_emissor,              # org_emissor
                uf_rg,                      # uf_4c
                cpf,                        # cpf
                num_registro,               # num_regis
                tipo,                       # categoria (mesma da prim_habi)
                nome_pai_sem_acentos,       # pai
                nome_mae_sem_acentos,       # mae
                assinatura                  # assinatura
            ])

    print(f"{qtd_itens} registros salvos em '{nome_arquivo}'")

if __name__ == "__main__":
    qtd = int(input("Quantos registros deseja gerar? "))
    gerar_csv(qtd)