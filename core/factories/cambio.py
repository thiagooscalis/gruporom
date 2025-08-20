import factory
from factory.django import DjangoModelFactory
from core.models import Cambio
from decimal import Decimal


class CambioFactory(DjangoModelFactory):
    class Meta:
        model = Cambio

    data = factory.Faker("date_this_year")
    valor = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=4,
        min_value=Decimal("3.0"),
        max_value=Decimal("6.0"),
    )
