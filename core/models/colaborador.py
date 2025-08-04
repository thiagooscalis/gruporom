# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .pessoa import Pessoa
from .cargo import Cargo
from .turno import Turno


class Colaborador(models.Model):
    """Model para colaboradores da empresa"""
    
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="colaborador",
        verbose_name="Pessoa"
    )
    
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        related_name="colaboradores",
        verbose_name="Cargo"
    )
    
    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Salário",
        help_text="Salário base do colaborador"
    )
    
    data_admissao = models.DateField(
        verbose_name="Data de Admissão"
    )
    
    data_demissao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Demissão"
    )
    
    gorjeta = models.BooleanField(
        default=False,
        verbose_name="Recebe Gorjeta",
        help_text="Indica se o colaborador recebe gorjetas"
    )
    
    comissao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Comissão (%)",
        help_text="Percentual de comissão sobre vendas"
    )
    
    turnos = models.ManyToManyField(
        Turno,
        blank=True,
        related_name="colaboradores",
        verbose_name="Turnos",
        help_text="Turnos que o colaborador pode trabalhar"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['pessoa__nome']
    
    def __str__(self):
        return f"{self.pessoa.nome} - {self.cargo.nome}"
    
    @property
    def nome(self):
        """Retorna o nome da pessoa do colaborador"""
        return self.pessoa.nome
    
    @property
    def documento(self):
        """Retorna o documento da pessoa do colaborador"""
        return self.pessoa.documento
    
    @property
    def empresa(self):
        """Retorna a empresa do cargo do colaborador"""
        return self.cargo.empresa
    
    @property
    def esta_ativo(self):
        """Verifica se o colaborador está ativo (não demitido)"""
        return self.ativo and self.data_demissao is None
    
    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        
        if self.data_demissao and self.data_admissao:
            if self.data_demissao <= self.data_admissao:
                raise ValidationError({
                    'data_demissao': 'A data de demissão deve ser posterior à data de admissão.'
                })
        
        if self.comissao and self.comissao > 100:
            raise ValidationError({
                'comissao': 'A comissão não pode ser maior que 100%.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)