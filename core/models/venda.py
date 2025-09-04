# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from decimal import Decimal
from .pessoa import Pessoa
from .bloqueio import Bloqueio
from .extra import Extra
from core.choices import (
    STATUS_VENDA_CHOICES,
    FORMA_PAGAMENTO_CHOICES,
    STATUS_PAGAMENTO_CHOICES
)
from core.managers.venda_manager import VendaBloqueioManager


class VendaBloqueio(models.Model):
    """
    Modelo para vendas de bloqueios (pacotes turísticos)
    """
    
    # Identificação
    codigo = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Código da Venda"
    )
    
    # Relacionamentos principais
    bloqueio = models.ForeignKey(
        Bloqueio,
        on_delete=models.PROTECT,
        related_name="vendas",
        verbose_name="Bloqueio"
    )
    
    cliente = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="vendas_bloqueio_cliente",
        verbose_name="Cliente",
        null=True,
        blank=True
    )
    
    vendedor = models.ForeignKey(
        'Usuario',
        on_delete=models.PROTECT,
        related_name="vendas_bloqueio_vendedor",
        verbose_name="Vendedor"
    )
    
    # Extras
    extras = models.ManyToManyField(
        Extra,
        through='ExtraVenda',
        related_name="vendas",
        blank=True,
        verbose_name="Extras"
    )
    
    # Status e datas
    status = models.CharField(
        max_length=30,
        choices=STATUS_VENDA_CHOICES,
        default='rascunho',
        verbose_name="Status"
    )
    
    data_venda = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data da Venda"
    )
    
    data_confirmacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Confirmação"
    )
    
    data_cancelamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Cancelamento"
    )
    
    data_viagem = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Viagem"
    )
    
    # Valores calculados
    valor_passageiros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total Passageiros"
    )
    
    valor_extras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total Extras"
    )
    
    valor_seguro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor do Seguro"
    )
    
    valor_taxas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor de Taxas"
    )
    
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Desconto"
    )
    
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total"
    )
    
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Pago"
    )
    
    valor_pendente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Pendente"
    )
    
    # Informações adicionais
    numero_passageiros = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Passageiros"
    )
    
    possui_seguro = models.BooleanField(
        default=False,
        verbose_name="Possui Seguro Viagem"
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    observacoes_internas = models.TextField(
        blank=True,
        verbose_name="Observações Internas"
    )
    
    motivo_cancelamento = models.TextField(
        blank=True,
        verbose_name="Motivo do Cancelamento"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    # Manager customizado
    objects = VendaBloqueioManager()
    
    class Meta:
        verbose_name = "Venda de Bloqueio"
        verbose_name_plural = "Vendas de Bloqueios"
        ordering = ["-data_venda"]
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['status']),
            models.Index(fields=['data_venda']),
            models.Index(fields=['cliente']),
            models.Index(fields=['bloqueio']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.gerar_codigo()
        
        # Recalcular totais antes de salvar
        self.calcular_totais()
        
        super().save(*args, **kwargs)
    
    def gerar_codigo(self):
        """Gera código único VB + ano + sequencial"""
        from django.db.models import Max
        ano = timezone.now().year
        prefixo = "VB"
        
        ultimo = VendaBloqueio.objects.filter(
            codigo__startswith=f"{prefixo}{ano}"
        ).aggregate(Max('codigo'))['codigo__max']
        
        if ultimo:
            try:
                sequencial = int(ultimo[6:]) + 1
            except:
                sequencial = 1
        else:
            sequencial = 1
        
        return f"{prefixo}{ano}{sequencial:05d}"
    
    def calcular_totais(self):
        """Recalcula todos os valores da venda"""
        # Calcula valor dos passageiros
        from .passageiro import Passageiro
        self.valor_passageiros = sum(
            p.valor_venda or Decimal('0') for p in self.passageiros.all()
        ) if self.pk else Decimal('0')
        
        # Calcula valor dos extras
        self.valor_extras = sum(
            ev.valor_total for ev in self.extravenda_set.all()
        ) if self.pk else Decimal('0')
        
        # Calcula valor total
        self.valor_total = (
            self.valor_passageiros + 
            self.valor_extras + 
            self.valor_seguro + 
            self.valor_taxas - 
            self.valor_desconto
        )
        
        # Calcula valor pago e pendente
        self.valor_pago = sum(
            p.valor for p in self.pagamentos.filter(status='confirmado')
        ) if self.pk else Decimal('0')
        
        self.valor_pendente = self.valor_total - self.valor_pago
        
        # Atualiza número de passageiros
        self.numero_passageiros = self.passageiros.count() if self.pk else 0
        
        # Atualiza status baseado nos pagamentos
        if self.valor_pendente <= 0 and self.valor_total > 0:
            if self.status in ['aguardando_pagamento', 'parcialmente_pago']:
                self.status = 'pago'
        elif self.valor_pago > 0:
            if self.status == 'aguardando_pagamento':
                self.status = 'parcialmente_pago'
    
    @property
    def pode_editar(self):
        """Verifica se a venda pode ser editada"""
        return self.status == 'pre-venda'
    
    @property
    def pode_adicionar_pagamento(self):
        """Verifica se pode adicionar pagamentos"""
        return self.status in ['pre-venda', 'confirmada'] and self.valor_pendente > 0
    
    @property
    def pode_cancelar(self):
        """Verifica se a venda pode ser cancelada"""
        return self.status in ['pre-venda', 'confirmada']
    
    @property
    def pode_confirmar(self):
        """Verifica se a venda pode ser confirmada"""
        # Venda deve estar em pré-venda
        if self.status != 'pre-venda':
            return False
        
        # Deve ter pelo menos um passageiro
        if not self.passageiros.exists():
            return False
        
        # Deve ter cliente (comprador) definido
        if not self.cliente_id:
            return False
        
        # Deve ter pelo menos um pagamento
        if not self.pagamentos.exists():
            return False
        
        return True
    
    @property
    def requisitos_confirmacao(self):
        """Retorna lista de requisitos pendentes para confirmação"""
        requisitos = []
        
        if not self.passageiros.exists():
            requisitos.append('Adicionar pelo menos um passageiro')
        
        if not self.cliente_id:
            requisitos.append('Definir o comprador/cliente')
        
        if not self.pagamentos.exists():
            requisitos.append('Registrar pelo menos um pagamento')
        
        if self.status != 'pre-venda':
            requisitos.append('Venda deve estar em status pré-venda')
        
        return requisitos
    
    @property
    def tem_passageiros(self):
        """Verifica se tem passageiros"""
        return self.passageiros.exists()
    
    @property
    def tem_pagamentos(self):
        """Verifica se tem pagamentos"""
        return self.pagamentos.exists()
    
    @property
    def tem_cliente(self):
        """Verifica se tem cliente/comprador definido"""
        return bool(self.cliente_id)
    
    @property
    def percentual_pago(self):
        """Retorna o percentual pago da venda"""
        if self.valor_total > 0:
            return (self.valor_pago / self.valor_total) * 100
        return 0
    
    @property
    def passageiros(self):
        """Retorna os passageiros relacionados a esta venda"""
        from .passageiro import Passageiro
        return Passageiro.objects.filter(venda=self)
    
    @property
    def status_display_pt(self):
        """Status da venda em português"""
        status_map = {
            'pre-venda': 'Pré-venda',
            'confirmada': 'Confirmada',
            'concluida': 'Concluída',
            'cancelada': 'Cancelada'
        }
        return status_map.get(self.status, self.get_status_display())
    
    @property
    def dias_ate_viagem(self):
        """Quantos dias até a data da viagem"""
        if hasattr(self.bloqueio, 'saida') and self.bloqueio.saida:
            hoje = timezone.now().date()
            return (self.bloqueio.saida - hoje).days
        return None
    
    @property
    def pode_alterar_passageiros(self):
        """Verifica se pode alterar passageiros"""
        return self.status in ['rascunho', 'orcamento'] and (
            not self.dias_ate_viagem or self.dias_ate_viagem > 7
        )
    
    @property
    def valor_formatado(self):
        """Valor total formatado para exibição"""
        return f"R$ {self.valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @property
    def valor_pendente_formatado(self):
        """Valor pendente formatado para exibição"""
        return f"R$ {self.valor_pendente:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @cached_property
    def resumo_passageiros(self):
        """Resumo dos passageiros (cached para performance)"""
        if not self.pk:
            return {'total': 0, 'tipos': {}}
            
        passageiros = self.passageiros.select_related('pessoa').values('tipo', 'pessoa__nome')
        
        resumo = {
            'total': len(passageiros),
            'nomes': [p['pessoa__nome'] for p in passageiros],
            'tipos': {}
        }
        
        for p in passageiros:
            tipo = p['tipo'] or 'Normal'
            resumo['tipos'][tipo] = resumo['tipos'].get(tipo, 0) + 1
            
        return resumo
    
    @cached_property
    def historico_pagamentos(self):
        """Histórico de pagamentos ordenado (cached)"""
        if not self.pk:
            return []
            
        return self.pagamentos.select_related().order_by('-data_pagamento')
    
    @property
    def proximo_vencimento(self):
        """Data do próximo pagamento vencendo (se houver parcelamento)"""
        # TODO: Implementar quando houver sistema de parcelas
        return None
    
    @property
    def css_status_class(self):
        """Classe CSS para o status (útil em templates)"""
        classes = {
            'pre-venda': 'warning',
            'confirmada': 'success',
            'concluida': 'primary',
            'cancelada': 'danger'
        }
        return classes.get(self.status, 'secondary')
    
    @property
    def pode_gerar_contrato(self):
        """Verifica se pode gerar contrato"""
        return self.status in ['confirmada', 'concluida'] and self.cliente
    
    @property
    def alerta_viagem_proxima(self):
        """Verifica se a viagem está próxima e precisa de atenção"""
        dias = self.dias_ate_viagem
        if dias is None:
            return False
        return dias <= 7 and dias >= 0 and self.status not in ['cancelada', 'concluida']


class ExtraVenda(models.Model):
    """
    Relacionamento entre Extra e Venda com quantidades
    """
    
    venda = models.ForeignKey(
        VendaBloqueio,
        on_delete=models.CASCADE,
        verbose_name="Venda"
    )
    
    extra = models.ForeignKey(
        Extra,
        on_delete=models.PROTECT,
        verbose_name="Extra"
    )
    
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade"
    )
    
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitário"
    )
    
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Desconto"
    )
    
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Total"
    )
    
    class Meta:
        verbose_name = "Extra da Venda"
        verbose_name_plural = "Extras da Venda"
        unique_together = [['venda', 'extra']]
        ordering = ['id']
    
    def __str__(self):
        return f"{self.extra.nome} x{self.quantidade}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = (self.valor_unitario * self.quantidade) - self.valor_desconto
        super().save(*args, **kwargs)
        
        # Atualizar totais da venda
        if self.venda:
            self.venda.calcular_totais()
            self.venda.save(update_fields=['valor_extras', 'valor_total', 'valor_pendente'])


class Pagamento(models.Model):
    """
    Modelo para pagamentos de vendas
    """
    
    # Relacionamento com venda
    venda = models.ForeignKey(
        VendaBloqueio,
        on_delete=models.CASCADE,
        related_name="pagamentos",
        verbose_name="Venda"
    )
    
    # Dados do pagamento
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name="Forma de Pagamento"
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor"
    )
    
    data_pagamento = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data do Pagamento"
    )
    
    data_confirmacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Confirmação"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_PAGAMENTO_CHOICES,
        default='pendente',
        verbose_name="Status"
    )
    
    # Informações adicionais
    parcela = models.PositiveIntegerField(
        default=1,
        verbose_name="Parcela"
    )
    
    total_parcelas = models.PositiveIntegerField(
        default=1,
        verbose_name="Total de Parcelas"
    )
    
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referência/Comprovante"
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-data_pagamento", "parcela"]
        indexes = [
            models.Index(fields=['venda', 'status']),
            models.Index(fields=['data_pagamento']),
        ]
    
    def __str__(self):
        return f"{self.get_forma_pagamento_display()} - R$ {self.valor} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Se confirmando o pagamento, atualiza data de confirmação
        if self.status == 'confirmado' and not self.data_confirmacao:
            self.data_confirmacao = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Atualizar totais da venda
        if self.venda:
            self.venda.calcular_totais()
            self.venda.save(update_fields=['valor_pago', 'valor_pendente', 'status'])