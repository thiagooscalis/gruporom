from django.db import models
from .bloqueio import Bloqueio
from core.choices import MOEDA_CHOICES


class Extra(models.Model):
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    moeda = models.CharField(max_length=10, choices=MOEDA_CHOICES, verbose_name="Moeda")
    bloqueio = models.ForeignKey(Bloqueio, on_delete=models.PROTECT, verbose_name="Bloqueio")
    
    class Meta:
        verbose_name = "Extra"
        verbose_name_plural = "Extras"
        ordering = ['descricao']
    
    def __str__(self):
        return f"{self.descricao} - {self.moeda} {self.valor}"