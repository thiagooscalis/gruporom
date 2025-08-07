from django.db import models
from .bloqueio import Bloqueio


class DiaRoteiro(models.Model):
    ordem = models.PositiveIntegerField(verbose_name="Ordem")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    bloqueio = models.ForeignKey(Bloqueio, on_delete=models.PROTECT, verbose_name="Bloqueio")
    
    class Meta:
        verbose_name = "Dia do Roteiro"
        verbose_name_plural = "Dias do Roteiro"
        ordering = ['bloqueio', 'ordem']
        unique_together = ['bloqueio', 'ordem']
    
    def __str__(self):
        return f"Dia {self.ordem}: {self.titulo}"