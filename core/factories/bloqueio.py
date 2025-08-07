import factory
from core.models import Bloqueio
from core.choices import MOEDA_CHOICES
from .caravana import CaravanaFactory
from .pais import PaisFactory
from .incluso import InclusoFactory
from .hotel import HotelFactory


class BloqueioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bloqueio
        skip_postgeneration_save = True
    
    caravana = factory.SubFactory(CaravanaFactory)
    descricao = factory.Faker('text', max_nb_chars=200)
    saida = factory.Faker('date_between', start_date='+1m', end_date='+1y')
    valor = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    taxas = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    moeda_valor = factory.Faker('random_element', elements=[choice[0] for choice in MOEDA_CHOICES])
    moeda_taxas = factory.Faker('random_element', elements=[choice[0] for choice in MOEDA_CHOICES])
    terrestre = factory.Faker('boolean', chance_of_getting_true=30)
    ativo = factory.Faker('boolean', chance_of_getting_true=80)
    
    @factory.post_generation
    def paises(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for pais in extracted:
                self.paises.add(pais)
        else:
            # Adicionar 1-3 países aleatórios
            import random
            paises_count = random.randint(1, 3)
            for _ in range(paises_count):
                self.paises.add(PaisFactory())
    
    @factory.post_generation
    def inclusos(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for incluso in extracted:
                self.inclusos.add(incluso)
        else:
            # Adicionar 3-8 itens inclusos aleatórios
            import random
            inclusos_count = random.randint(3, 8)
            for _ in range(inclusos_count):
                self.inclusos.add(InclusoFactory())
    
    @factory.post_generation
    def hoteis(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for hotel in extracted:
                self.hoteis.add(hotel)
        else:
            # Adicionar 1-4 hotéis aleatórios
            import random
            hoteis_count = random.randint(1, 4)
            for _ in range(hoteis_count):
                self.hoteis.add(HotelFactory())
        self.save()