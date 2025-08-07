import factory
from core.models import DiaRoteiro
from .bloqueio import BloqueioFactory


class DiaRoteiroFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DiaRoteiro
    
    ordem = factory.Sequence(lambda n: n + 1)
    titulo = factory.Faker('sentence', nb_words=4)
    descricao = factory.Faker('text', max_nb_chars=500)
    bloqueio = factory.SubFactory(BloqueioFactory)