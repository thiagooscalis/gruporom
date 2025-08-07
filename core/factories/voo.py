import factory
from datetime import timedelta
from django.utils import timezone
from core.models import Voo
from .cia_area import CiaAreaFactory
from .aeroporto import AeroportoFactory
from .bloqueio import BloqueioFactory


class VooFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Voo
    
    numero = factory.Faker('bothify', text='??####', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    cia_aerea = factory.SubFactory(CiaAreaFactory)
    embarque = factory.Faker('date_time_between', start_date='+1d', end_date='+6m', tzinfo=timezone.get_current_timezone())
    aeroporto_embarque = factory.SubFactory(AeroportoFactory)
    aeroporto_desembarque = factory.SubFactory(AeroportoFactory)
    bloqueio = factory.SubFactory(BloqueioFactory)
    
    @factory.lazy_attribute
    def desembarque(self):
        # Desembarque entre 1-12 horas após o embarque
        import random
        horas_voo = random.randint(1, 12)
        return self.embarque + timedelta(hours=horas_voo)