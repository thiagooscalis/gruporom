import factory
from core.models import Hotel
from .cidade import CidadeFactory


class HotelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hotel
    
    nome = factory.Faker('company', locale='pt_BR')
    endereco = factory.Faker('address', locale='pt_BR')
    telefone = factory.Faker('phone_number', locale='pt_BR')
    cidade = factory.SubFactory(CidadeFactory)