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
    return ''.join([str(random.randint(0, 9)) for _ in range(11)])

def gerar_rg():
    return f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"

def gerar_orgao_emissor():
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
            data_nascimento = fake.date_of_birth(minimum_age=18, maximum_age=80)
            data_nasci_formatada = data_nascimento.strftime("%d/%m/%Y")                      
            local_nascimento = remover_acentos(fake.city())
            uf_nascimento = random.choice(estados_br)
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
            
            assinatura = nome_sem_acentos

            escritor.writerow([
                nome_sem_acentos,           
                tipo,                        
                data_nasci_formatada,       
                local_nascimento,           
                uf_nascimento,              
                data_emissao_formatada,     
                validade_formatada,         
                rg,                         
                orgao_emissor,              
                uf_rg,                      
                cpf,                        
                num_registro,               
                tipo,                       
                nome_pai_sem_acentos,       
                nome_mae_sem_acentos,       
                assinatura                  
            ])

    print(f"{qtd_itens} registros salvos em '{nome_arquivo}'")

if __name__ == "__main__":
    qtd = int(input("Quantos registros deseja gerar? "))
    gerar_csv(qtd)