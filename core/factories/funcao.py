import factory
from factory.django import DjangoModelFactory
from core.models import Funcao


class FuncaoFactory(DjangoModelFactory):
    class Meta:
        model = Funcao
    
    masculino = factory.Faker('job', locale='pt_BR')
    feminino = factory.LazyAttribute(lambda obj: obj.masculino.replace('o', 'a') if obj.masculino.endswith('o') else obj.masculino)
    abreviacao_masculino = factory.LazyAttribute(lambda obj: obj.masculino[:3].upper())
    abreviacao_feminino = factory.LazyAttribute(lambda obj: obj.feminino[:3].upper())