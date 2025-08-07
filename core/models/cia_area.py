from django.db import models


class CiaArea(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Companhia Aérea")
    iata = models.CharField(max_length=3, unique=True, verbose_name="Código IATA")
    
    class Meta:
        verbose_name = "Companhia Aérea"
        verbose_name_plural = "Companhias Aéreas"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.iata})"