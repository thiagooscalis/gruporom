import factory
from factory.django import DjangoModelFactory
from core.models import Turno
from datetime import time
import random


class TurnoFactory(DjangoModelFactory):
    class Meta:
        model = Turno
    
    nome = factory.Sequence(lambda n: f"Turno {n}")
    inicio = factory.Faker('time_object')
    fim = factory.Faker('time_object')
    
    ativo = True