from django.db import models
from .pessoa import Pessoa
from core.choices import TIPO_EMPRESA_CHOICES


class Fornecedor(models.Model):
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.PROTECT,
        verbose_name="Pessoa",
        related_name="fornecedor"
    )
    tipo_empresa = models.CharField(
        max_length=50,
        choices=TIPO_EMPRESA_CHOICES,
        verbose_name="Tipo de Empresa"
    )
    empresas = models.ManyToManyField(
        Pessoa,
        limit_choices_to={'empresa_gruporom': True},
        verbose_name="Empresas do Grupo ROM",
        related_name="fornecedores_relacionados"
    )

    class Meta:
        ordering = ["pessoa__nome"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return f"{self.pessoa.nome} - {self.tipo_empresa}"
