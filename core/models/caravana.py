from django.db import models
from .pessoa import Pessoa
from core.choices import TIPO_CARAVANA_CHOICES, REPASSE_TIPO_CHOICES


class Caravana(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Caravana")
    empresa = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="caravanas_empresa",
        verbose_name="Empresa",
    )
    promotor = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="caravanas_promotor",
        verbose_name="Promotor",
    )
    responsavel = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="caravanas_responsavel",
        verbose_name="Responsável",
    )
    lideres = models.ManyToManyField(
        Pessoa,
        related_name="caravanas_lideres",
        verbose_name="Líderes",
        blank=True,
    )
    tipo = models.CharField(
        max_length=20, choices=TIPO_CARAVANA_CHOICES, verbose_name="Tipo"
    )
    link = models.URLField(blank=True, null=True, verbose_name="Link")
    destaque_site = models.IntegerField(
        default=0, verbose_name="Destaque no Site"
    )
    repasse_valor = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor do Repasse"
    )
    repasse_tipo = models.CharField(
        max_length=20,
        choices=REPASSE_TIPO_CHOICES,
        verbose_name="Tipo de Repasse",
    )
    banner_site = models.ImageField(
        upload_to="caravanas/banners/",
        blank=True,
        null=True,
        verbose_name="Banner do Site",
    )
    banner_mobile = models.ImageField(
        upload_to="caravanas/banners_mobile/",
        blank=True,
        null=True,
        verbose_name="Banner Mobile",
    )
    quantidade = models.PositiveIntegerField(
        verbose_name="Quantidade de Passageiros"
    )
    free_economica = models.PositiveIntegerField(
        default=0, verbose_name="Free Econômica"
    )
    free_executiva = models.PositiveIntegerField(
        default=0, verbose_name="Free Executiva"
    )
    data_contrato = models.DateField(verbose_name="Data do Contrato")

    class Meta:
        verbose_name = "Caravana"
        verbose_name_plural = "Caravanas"
        ordering = ["-data_contrato", "nome"]

    def __str__(self):
        return self.nome

    @property
    def lideres_nomes(self):
        """Retorna uma string com os nomes dos líderes separados por vírgula"""
        try:
            return ", ".join([lider.nome for lider in self.lideres.all()])
        except:
            return ""
