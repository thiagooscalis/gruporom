from django.db import models
from django.utils import timezone
from .usuario import Usuario


class Nota(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Usuário")
    descricao = models.TextField(verbose_name="Descrição")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Criada em")
    resposta = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, verbose_name="Resposta para")
    
    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        ordering = ['-created_at']
    
    def __str__(self):
        prefix = "↳ " if self.resposta else ""
        return f"{prefix}{self.usuario.pessoa.nome}: {self.descricao[:50]}..."