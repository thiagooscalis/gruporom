from django.db import models
from .pessoa import Pessoa
from .bloqueio import Bloqueio
from core.choices import TIPO_PASSAGEIRO_CHOICES


class Passageiro(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, verbose_name="Pessoa")
    bloqueio = models.ForeignKey(Bloqueio, on_delete=models.PROTECT, verbose_name="Bloqueio")
    tipo = models.CharField(max_length=10, choices=TIPO_PASSAGEIRO_CHOICES, blank=True, null=True, verbose_name="Tipo")
    single = models.BooleanField(default=False, verbose_name="Single")
    
    class Meta:
        verbose_name = "Passageiro"
        verbose_name_plural = "Passageiros"
        ordering = ['pessoa__nome']
        unique_together = ['pessoa', 'bloqueio']
    
    def __str__(self):
        tipo_str = f" - {self.tipo}" if self.tipo else ""
        return f"{self.pessoa.nome}{tipo_str}"