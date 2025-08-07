import factory
from core.models import Incluso


class InclusoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Incluso
    
    descricao = factory.Faker('sentence', nb_words=4)
    incluso = factory.Faker('boolean')
    padrao = factory.Faker('boolean', chance_of_getting_true=20)  # 20% chance de ser padrão