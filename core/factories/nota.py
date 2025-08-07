import factory
from django.utils import timezone
from core.models import Nota
from .usuario import UsuarioFactory


class NotaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Nota
    
    usuario = factory.SubFactory(UsuarioFactory)
    descricao = factory.Faker('text', max_nb_chars=500)
    created_at = factory.Faker('date_time_between', start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
    resposta = None  # Por padrão, não é resposta


class NotaRespostaFactory(NotaFactory):
    """Factory para criar notas que são respostas"""
    resposta = factory.SubFactory(NotaFactory)