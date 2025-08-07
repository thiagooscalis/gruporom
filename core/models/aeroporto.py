from django.db import models
from .cidade import Cidade


class Aeroporto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Aeroporto")
    iata = models.CharField(max_length=3, unique=True, verbose_name="Código IATA")
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, verbose_name="Cidade")
    timezone = models.CharField(max_length=50, verbose_name="Fuso Horário")
    
    class Meta:
        verbose_name = "Aeroporto"
        verbose_name_plural = "Aeroportos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.iata}) - {self.cidade}"