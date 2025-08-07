import factory
from factory.django import DjangoModelFactory
from core.models import Pessoa
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES, TIPO_EMPRESA_CHOICES


class PessoaFactory(DjangoModelFactory):
    class Meta:
        model = Pessoa

    tipo_doc = "CPF"
    doc = factory.Sequence(lambda n: f"{n:011d}")
    nome = factory.Faker("name", locale="pt_BR")
    # apelido não existe no model atual
    sexo = factory.Iterator(["Masculino", "Feminino"])
    nascimento = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    email = factory.Faker("email")
    telefone = factory.Faker("phone_number", locale="pt_BR")
    # celular não existe no model atual
    
    # Endereço
    cep = factory.Faker("postcode", locale="pt_BR")
    endereco = factory.Faker("street_name", locale="pt_BR")
    numero = factory.Faker("building_number", locale="pt_BR")
    bairro = factory.Faker("bairro", locale="pt_BR")
    cidade = factory.Faker("city", locale="pt_BR")
    estado = factory.Faker("estado_sigla", locale="pt_BR")
    
    # is_active não existe no model Pessoa


class PessoaJuridicaFactory(PessoaFactory):
    """Factory para Pessoa Jurídica (CNPJ)"""
    
    tipo_doc = "CNPJ"
    doc = factory.Sequence(lambda n: f"{n:014d}")
    nome = factory.Faker("company", locale="pt_BR")
    # apelido não existe no model atual
    sexo = None
    nascimento = None
    email = factory.LazyAttribute(lambda obj: f"contato@{obj.nome.lower().replace(' ', '').replace('.', '')}.com.br")


class EmpresaGrupoROMFactory(PessoaJuridicaFactory):
    """Factory para Empresa do Grupo ROM"""
    
    empresa_gruporom = True
    tipo_empresa = factory.Iterator([choice[0] for choice in TIPO_EMPRESA_CHOICES])
    

class PessoaComPassaporteFactory(PessoaFactory):
    """Factory para Pessoa com dados de passaporte"""
    
    passaporte_numero = factory.Faker("bothify", text="??######")
    passaporte_pais = factory.Faker("country_code")
    passaporte_validade = factory.Faker("date_between", start_date="+1y", end_date="+10y")