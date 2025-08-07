from django.db import models


class Pais(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do País")
    iso = models.CharField(max_length=2, unique=True, verbose_name="Código ISO")
    
    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.iso})"