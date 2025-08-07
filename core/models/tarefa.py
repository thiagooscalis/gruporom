from django.db import models
from django.utils import timezone
from .bloqueio import Bloqueio
from core.choices import CATEGORIA_TAREFA_CHOICES


class Tarefa(models.Model):
    categoria = models.CharField(max_length=20, choices=CATEGORIA_TAREFA_CHOICES, verbose_name="Categoria")
    descricao = models.CharField(max_length=500, verbose_name="Descrição")
    bloqueio = models.ForeignKey(Bloqueio, on_delete=models.PROTECT, verbose_name="Bloqueio")
    concluida_em = models.DateTimeField(blank=True, null=True, verbose_name="Concluída em")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criada em")
    
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['-created_at']
    
    @property
    def concluida(self):
        return self.concluida_em is not None
    
    def __str__(self):
        status = "✓" if self.concluida else "○"
        return f"{status} [{self.categoria}] {self.descricao}"