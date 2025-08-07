from django.db import models
from .cia_area import CiaArea
from .aeroporto import Aeroporto
from .bloqueio import Bloqueio


class Voo(models.Model):
    numero = models.CharField(max_length=20, verbose_name="Número do Voo")
    cia_aerea = models.ForeignKey(CiaArea, on_delete=models.PROTECT, verbose_name="Companhia Aérea")
    embarque = models.DateTimeField(verbose_name="Data/Hora de Embarque")
    desembarque = models.DateTimeField(verbose_name="Data/Hora de Desembarque")
    aeroporto_embarque = models.ForeignKey(Aeroporto, on_delete=models.PROTECT, related_name="voos_embarque", verbose_name="Aeroporto de Embarque")
    aeroporto_desembarque = models.ForeignKey(Aeroporto, on_delete=models.PROTECT, related_name="voos_desembarque", verbose_name="Aeroporto de Desembarque")
    bloqueio = models.ForeignKey(Bloqueio, on_delete=models.PROTECT, verbose_name="Bloqueio")
    
    class Meta:
        verbose_name = "Voo"
        verbose_name_plural = "Voos"
        ordering = ['embarque']
    
    def __str__(self):
        return f"{self.cia_aerea.iata} {self.numero} - {self.aeroporto_embarque.iata} → {self.aeroporto_desembarque.iata}"