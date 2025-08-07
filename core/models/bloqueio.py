from django.db import models
from .caravana import Caravana
from .pais import Pais
from .incluso import Incluso
from .hotel import Hotel
from core.choices import MOEDA_CHOICES


class Bloqueio(models.Model):
    caravana = models.ForeignKey(Caravana, on_delete=models.PROTECT, verbose_name="Caravana")
    descricao = models.CharField(max_length=500, verbose_name="Descrição")
    saida = models.DateField(verbose_name="Data de Saída")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    taxas = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Taxas")
    moeda_valor = models.CharField(max_length=10, choices=MOEDA_CHOICES, verbose_name="Moeda do Valor")
    moeda_taxas = models.CharField(max_length=10, choices=MOEDA_CHOICES, verbose_name="Moeda das Taxas")
    paises = models.ManyToManyField(Pais, verbose_name="Países", blank=True)
    inclusos = models.ManyToManyField(Incluso, verbose_name="Itens Inclusos", blank=True)
    hoteis = models.ManyToManyField(Hotel, verbose_name="Hotéis", blank=True)
    terrestre = models.BooleanField(default=False, verbose_name="Terrestre")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Bloqueio"
        verbose_name_plural = "Bloqueios"
        ordering = ['saida']
    
    def __str__(self):
        return f"{self.caravana.nome} - {self.descricao} ({self.saida})"