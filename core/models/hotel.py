from django.db import models
from .cidade import Cidade


class Hotel(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Hotel")
    endereco = models.CharField(max_length=500, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    foto = models.ImageField(upload_to='hoteis/', blank=True, null=True, verbose_name="Foto")
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, verbose_name="Cidade")
    
    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hotéis"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.cidade}"