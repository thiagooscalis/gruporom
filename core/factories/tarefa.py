import factory
from django.utils import timezone
from core.models import Tarefa
from core.choices import CATEGORIA_TAREFA_CHOICES
from .bloqueio import BloqueioFactory


class TarefaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tarefa
    
    categoria = factory.Faker('random_element', elements=[choice[0] for choice in CATEGORIA_TAREFA_CHOICES])
    descricao = factory.Faker('sentence', nb_words=8)
    bloqueio = factory.SubFactory(BloqueioFactory)
    concluida_em = factory.Faker('date_time_between', start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
    created_at = factory.Faker('date_time_between', start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone())