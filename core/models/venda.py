from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from core.choices import STATUS_VENDA_CHOICES

User = get_user_model()


class VendaBase(models.Model):
    """Model abstrato base para vendas"""
    
    # Cliente e vendedor
    cliente = models.ForeignKey(
        'Pessoa',
        on_delete=models.PROTECT,
        related_name='%(class)s_como_cliente',
        verbose_name="Cliente",
        null=True,
        blank=True
    )
    vendedor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(class)s_realizadas',
        verbose_name="Vendedor"
    )
    
    # Status e datas
    status = models.CharField(
        max_length=30,
        choices=STATUS_VENDA_CHOICES,
        default='rascunho',
        verbose_name="Status"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    data_confirmacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Confirmação"
    )
    
    # Valores
    valor_produtos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor de Produtos"
    )
    valor_servicos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor de Serviços"
    )
    valor_extras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor de Extras"
    )
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor de Desconto"
    )
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Total"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    # Controle
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        abstract = True
        ordering = ['-data_criacao']
    
    def calcular_total(self):
        """Calcula o valor total da venda"""
        subtotal = self.valor_produtos + self.valor_servicos + self.valor_extras
        self.valor_total = subtotal - self.valor_desconto
        return self.valor_total
    
    def save(self, *args, **kwargs):
        # Calcula o total antes de salvar
        self.calcular_total()
        super().save(*args, **kwargs)


class VendaBloqueio(VendaBase):
    """Venda específica para bloqueios de caravanas"""
    
    # Relacionamento com bloqueio
    bloqueio = models.ForeignKey(
        'Bloqueio',
        on_delete=models.PROTECT,
        related_name='vendas',
        verbose_name="Bloqueio"
    )
    
    # Quantidade de passageiros
    quantidade_passageiros = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade de Passageiros"
    )
    
    # Valor unitário do bloqueio
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Unitário"
    )
    
    class Meta:
        verbose_name = "Venda de Bloqueio"
        verbose_name_plural = "Vendas de Bloqueios"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Venda #{self.id} - {self.bloqueio.caravana.nome}"
    
    def calcular_total(self):
        """Calcula o valor total da venda baseado na quantidade de passageiros"""
        self.valor_produtos = self.valor_unitario * self.quantidade_passageiros
        return super().calcular_total()
    
    def save(self, *args, **kwargs):
        # Atualiza o valor unitário baseado no bloqueio se não foi definido
        if not self.valor_unitario and self.bloqueio:
            self.valor_unitario = self.bloqueio.valor_convertido
        
        super().save(*args, **kwargs)