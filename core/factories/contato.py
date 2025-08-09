import factory
from factory.django import DjangoModelFactory
from core.models import Telefone, Email


class TelefoneFactory(DjangoModelFactory):
    class Meta:
        model = Telefone

    ddi = '55'
    ddd = factory.Iterator(['11', '21', '85', '62', '47', '51'])
    telefone = factory.Sequence(lambda n: f"9{n:08d}")
    tipo = factory.Iterator(['celular', 'residencial', 'comercial'])
    principal = False
    ativo = True


class EmailFactory(DjangoModelFactory):
    class Meta:
        model = Email

    email = factory.Faker('email')
    tipo = factory.Iterator(['pessoal', 'profissional', 'comercial'])
    principal = False
    ativo = True
    verificado = False