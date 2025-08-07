import factory
from core.models import Extra
from core.choices import MOEDA_CHOICES
from .bloqueio import BloqueioFactory


class ExtraFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Extra
    
    descricao = factory.Faker('sentence', nb_words=5)
    valor = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    moeda = factory.Faker('random_element', elements=[choice[0] for choice in MOEDA_CHOICES])
    bloqueio = factory.SubFactory(BloqueioFactory)