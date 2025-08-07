import factory
from core.models import Passageiro
from core.choices import TIPO_PASSAGEIRO_CHOICES
from .pessoa import PessoaFactory
from .bloqueio import BloqueioFactory


class PassageiroFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Passageiro
    
    pessoa = factory.SubFactory(PessoaFactory)
    bloqueio = factory.SubFactory(BloqueioFactory)
    tipo = factory.Faker('random_element', elements=[None] + [choice[0] for choice in TIPO_PASSAGEIRO_CHOICES])
    single = factory.Faker('boolean', chance_of_getting_true=25)