import factory
from factory.django import DjangoModelFactory
from core.models import Cargo


class CargoFactory(DjangoModelFactory):
    class Meta:
        model = Cargo
    
    nome = factory.Faker('job', locale='pt_BR')
    empresa = factory.SubFactory('core.factories.EmpresaGrupoROMFactory')
    ativo = True