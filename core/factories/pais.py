import factory
from core.models import Pais


class PaisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pais
        django_get_or_create = ('iso',)
    
    nome = factory.Faker('country', locale='pt_BR')
    iso = factory.Faker('country_code')