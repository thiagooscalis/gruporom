from django.db import models
from datetime import date
from decimal import Decimal
from .caravana import Caravana
from .pais import Pais
from .incluso import Incluso
from .hotel import Hotel
from .cambio import Cambio
from core.choices import MOEDA_CHOICES


class Bloqueio(models.Model):
    caravana = models.ForeignKey(Caravana, on_delete=models.PROTECT, verbose_name="Caravana")
    descricao = models.CharField(max_length=500, verbose_name="Descrição")
    saida = models.DateField(verbose_name="Data de Saída")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    taxas = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Taxas")
    moeda_valor = models.CharField(max_length=10, choices=MOEDA_CHOICES, verbose_name="Moeda do Valor")
    moeda_taxas = models.CharField(max_length=10, choices=MOEDA_CHOICES, verbose_name="Moeda das Taxas")
    paises = models.ManyToManyField(Pais, verbose_name="Países", blank=True)
    inclusos = models.ManyToManyField(Incluso, verbose_name="Itens Inclusos", blank=True)
    hoteis = models.ManyToManyField(Hotel, verbose_name="Hotéis", blank=True)
    terrestre = models.BooleanField(default=False, verbose_name="Terrestre")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Bloqueio"
        verbose_name_plural = "Bloqueios"
        ordering = ['saida']
    
    def __str__(self):
        return f"{self.caravana.nome} - {self.descricao} ({self.saida})"
    
    @property
    def valor_convertido(self):
        """
        Retorna o valor total (valor + taxas) convertido para reais
        usando o câmbio do dia atual
        """
        try:
            # Obtém o câmbio do dia
            cambio = Cambio.obter_cambio(date.today())
            if not cambio:
                return None
            
            dolar_hoje = cambio.valor
            
            # Converte valor para reais
            if self.moeda_valor == 'Dólar':
                valor_reais = self.valor * dolar_hoje
            elif self.moeda_valor == 'Real':
                valor_reais = self.valor
            else:
                # Se houver outras moedas no futuro
                valor_reais = self.valor
            
            # Converte taxas para reais
            if self.moeda_taxas == 'Dólar':
                taxas_reais = self.taxas * dolar_hoje
            elif self.moeda_taxas == 'Real':
                taxas_reais = self.taxas
            else:
                # Se houver outras moedas no futuro
                taxas_reais = self.taxas
            
            # Retorna a soma total em reais
            return Decimal(valor_reais + taxas_reais).quantize(Decimal('0.01'))
            
        except Exception:
            return None
    
    @property
    def valor_em_reais(self):
        """
        Retorna apenas o valor (sem taxas) convertido para reais
        """
        try:
            if self.moeda_valor == 'Real':
                return self.valor
            
            cambio = Cambio.obter_cambio(date.today())
            if not cambio:
                return self.valor
            
            if self.moeda_valor == 'Dólar':
                return Decimal(self.valor * cambio.valor).quantize(Decimal('0.01'))
            
            return self.valor
        except Exception:
            return self.valor
    
    @property
    def taxas_em_reais(self):
        """
        Retorna apenas as taxas convertidas para reais
        """
        try:
            if self.moeda_taxas == 'Real':
                return self.taxas
            
            cambio = Cambio.obter_cambio(date.today())
            if not cambio:
                return self.taxas
            
            if self.moeda_taxas == 'Dólar':
                return Decimal(self.taxas * cambio.valor).quantize(Decimal('0.01'))
            
            return self.taxas
        except Exception:
            return self.taxas