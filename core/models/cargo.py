# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError


class Cargo(models.Model):
    """
    Model para representar cargos nas empresas do Grupo ROM
    """
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome do Cargo",
        help_text="Ex: Diretor Executivo, Gerente de Vendas, Analista de Marketing"
    )
    empresa = models.ForeignKey(
        'Pessoa',
        on_delete=models.PROTECT,
        limit_choices_to={'empresa_gruporom': True},
        related_name='cargos',
        verbose_name="Empresa",
        help_text="Empresa do Grupo ROM onde o cargo existe"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Cargos inativos não aparecem em novas seleções"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['empresa', 'nome']
        unique_together = [['nome', 'empresa']]  # Não pode ter cargo repetido na mesma empresa

    def __str__(self):
        return f"{self.nome} - {self.empresa.nome}"

    def clean(self):
        """Validações customizadas"""
        if self.nome:
            self.nome = self.nome.strip().title()
            
        # Valida se é realmente uma empresa do Grupo ROM
        if self.empresa and not self.empresa.empresa_gruporom:
            raise ValidationError("O cargo deve ser vinculado a uma empresa do Grupo ROM.")

    def save(self, *args, **kwargs):
        """Override save para executar clean"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_funcionarios(self):
        """Retorna total de funcionários com este cargo"""
        # Será implementado quando houver model de funcionários
        return 0