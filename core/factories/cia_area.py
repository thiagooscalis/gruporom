import factory
from core.models import CiaArea


class CiaAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CiaArea
        django_get_or_create = ('iata',)
    
    nome = factory.Faker('company', locale='pt_BR')
    iata = factory.Faker('lexify', text='???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')