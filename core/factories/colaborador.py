import factory
from factory.django import DjangoModelFactory
from core.models import Colaborador
from decimal import Decimal


class ColaboradorFactory(DjangoModelFactory):
    class Meta:
        model = Colaborador
        skip_postgeneration_save = True
    
    pessoa = factory.SubFactory('core.factories.PessoaFactory')
    cargo = factory.SubFactory('core.factories.CargoFactory')
    salario = factory.Faker('pydecimal', left_digits=5, right_digits=2, min_value=Decimal('1500.00'), max_value=Decimal('10000.00'))
    data_admissao = factory.Faker('date_between', start_date='-2y', end_date='today')
    data_demissao = None
    gorjeta = factory.Faker('boolean')
    comissao = factory.Faker('pydecimal', left_digits=2, right_digits=2, min_value=Decimal('0.00'), max_value=Decimal('20.00'))
    ativo = True
    
    @factory.post_generation
    def turnos(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for turno in extracted:
                self.turnos.add(turno)
        else:
            # Adiciona 1-2 turnos aleatórios
            from core.factories import TurnoFactory
            import random
            turnos = TurnoFactory.create_batch(random.randint(1, 2))
            for turno in turnos:
                self.turnos.add(turno)