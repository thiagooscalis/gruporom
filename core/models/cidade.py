from django.db import models
from .pais import Pais


class Cidade(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Cidade")
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, verbose_name="País")
    
    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome}, {self.pais.nome}"