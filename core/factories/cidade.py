import factory
from core.models import Cidade
from .pais import PaisFactory


class CidadeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cidade
    
    nome = factory.Faker('city', locale='pt_BR')
    pais = factory.SubFactory(PaisFactory)