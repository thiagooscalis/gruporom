import factory
from factory.django import DjangoModelFactory
from core.models import Pessoa
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES, TIPO_EMPRESA_CHOICES
import random


class PessoaFactory(DjangoModelFactory):
    class Meta:
        model = Pessoa

    tipo_doc = "CPF"
    doc = factory.Sequence(lambda n: f"{n:011d}")
    nome = factory.Faker("name", locale="pt_BR")
    sexo = factory.Iterator(["Masculino", "Feminino"])
    nascimento = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    
    # Endereço
    cep = factory.Faker("postcode", locale="pt_BR")
    endereco = factory.Faker("street_name", locale="pt_BR")
    numero = factory.Faker("building_number", locale="pt_BR")
    bairro = factory.Faker("bairro", locale="pt_BR")
    cidade = factory.Faker("city", locale="pt_BR")
    estado = factory.Faker("estado_sigla", locale="pt_BR")
    
    # Campos de email diretos
    email1 = factory.Faker("email")
    email2 = factory.LazyFunction(lambda: factory.Faker("email").evaluate(None, None, {'locale': None}) if random.choice([True, False]) else "")
    email3 = factory.LazyFunction(lambda: factory.Faker("email").evaluate(None, None, {'locale': None}) if random.choice([True, False]) else "")
    
    # Campos de telefone diretos - Telefone 1 (obrigatório)
    ddi1 = "55"
    ddd1 = factory.Faker("random_element", elements=["11", "21", "31", "41", "51", "61", "71", "81", "85"])
    telefone1 = factory.LazyFunction(lambda: f"9{random.randint(10000000, 99999999)}")
    
    # Telefone 2 (opcional)
    ddi2 = factory.LazyFunction(lambda: "55" if random.choice([True, False]) else None)
    ddd2 = factory.LazyFunction(lambda: factory.Faker("random_element", elements=["11", "21", "31", "41", "51", "61", "71", "81", "85"]).evaluate(None, None, {'locale': None}) if random.choice([True, False]) else None)
    telefone2 = factory.LazyFunction(lambda: f"9{random.randint(10000000, 99999999)}" if random.choice([True, False]) else None)


class PessoaJuridicaFactory(PessoaFactory):
    """Factory para Pessoa Jurídica (CNPJ)"""
    
    tipo_doc = "CNPJ"
    doc = factory.Sequence(lambda n: f"{n:014d}")
    nome = factory.Faker("company", locale="pt_BR")
    sexo = None
    nascimento = None
    
    # Override para email comercial
    email1 = factory.LazyAttribute(lambda obj: f"contato@{obj.nome.lower().replace(' ', '').replace('.', '').replace(',', '').replace('-', '').replace('(', '').replace(')', '')}".replace('ltda', '') + "ltda.com.br")
    telefone1 = factory.LazyFunction(lambda: f"{random.randint(30000000, 39999999)}")  # Telefone comercial


class EmpresaGrupoROMFactory(PessoaJuridicaFactory):
    """Factory para Empresa do Grupo ROM"""
    
    empresa_gruporom = True
    tipo_empresa = factory.Iterator([choice[0] for choice in TIPO_EMPRESA_CHOICES])
    

class PessoaComPassaporteFactory(PessoaFactory):
    """Factory para Pessoa com dados de passaporte"""
    
    passaporte_numero = factory.Faker("bothify", text="??######")
    passaporte_pais = factory.Faker("country_code")
    passaporte_validade = factory.Faker("date_between", start_date="+1y", end_date="+10y")