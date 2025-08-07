import factory
from core.models import Caravana
from core.choices import TIPO_CARAVANA_CHOICES, REPASSE_TIPO_CHOICES
from .pessoa import PessoaFactory


class CaravanaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Caravana
        skip_postgeneration_save = True
    
    nome = factory.Faker('sentence', nb_words=3)
    empresa = factory.SubFactory(PessoaFactory)
    promotor = factory.SubFactory(PessoaFactory)
    tipo = factory.Faker('random_element', elements=[choice[0] for choice in TIPO_CARAVANA_CHOICES])
    link = factory.Faker('url')
    destaque_site = factory.Faker('random_int', min=0, max=10)
    repasse_valor = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    repasse_tipo = factory.Faker('random_element', elements=[choice[0] for choice in REPASSE_TIPO_CHOICES])
    quantidade = factory.Faker('random_int', min=10, max=100)
    free_economica = factory.Faker('random_int', min=0, max=5)
    free_executiva = factory.Faker('random_int', min=0, max=2)
    data_contrato = factory.Faker('date_this_year')
    
    @factory.post_generation
    def lideres(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for lider in extracted:
                self.lideres.add(lider)
        else:
            # Adicionar 1-3 líderes aleatórios
            import random
            lideres_count = random.randint(1, 3)
            for _ in range(lideres_count):
                self.lideres.add(PessoaFactory())
        self.save()