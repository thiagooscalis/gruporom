import factory
from core.models import Aeroporto
from .cidade import CidadeFactory


class AeroportoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Aeroporto
        django_get_or_create = ('iata',)
    
    nome = factory.Faker('sentence', nb_words=3)
    iata = factory.Faker('lexify', text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    cidade = factory.SubFactory(CidadeFactory)
    timezone = factory.Faker('timezone')