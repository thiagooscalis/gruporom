from django.db import models


class Incluso(models.Model):
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    incluso = models.BooleanField(verbose_name="Incluso")
    padrao = models.BooleanField(default=False, verbose_name="Padrão")
    
    class Meta:
        verbose_name = "Item Incluso"
        verbose_name_plural = "Itens Inclusos"
        ordering = ['-incluso', 'descricao']
    
    def __str__(self):
        status = "Incluso" if self.incluso else "Não Incluso"
        return f"{self.descricao} - {status}"