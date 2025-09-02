# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Count, Sum, F, Q, Case, When, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal


class VendaBloqueioManager(models.Manager):
    """
    Manager customizado para VendaBloqueio com queries otimizadas
    """
    
    def com_dados_completos(self):
        """
        Query otimizada com todos os relacionamentos e cálculos necessários
        Evita N+1 queries ao buscar vendas
        """
        return self.select_related(
            'cliente',
            'bloqueio',
            'vendedor'
        ).prefetch_related(
            'passageiros',
            'extras',
            'pagamentos'
        )
    
    def com_totais_calculados(self):
        """
        Adiciona cálculos agregados diretamente na query
        Mais eficiente que usar properties para listagens
        """
        return self.com_dados_completos().annotate(
            # Contadores
            total_passageiros_count=Count('passageiros'),
            total_pagamentos_count=Count('pagamentos'),
            
            # Valores calculados
            total_pago_calculado=Coalesce(
                Sum('pagamentos__valor', filter=Q(pagamentos__status='confirmado')),
                Value(Decimal('0'))
            ),
            total_pendente_calculado=F('valor_total') - F('total_pago_calculado'),
            
            # Status derivado baseado em pagamentos
            status_pagamento=Case(
                When(total_pago_calculado__gte=F('valor_total'), then=Value('pago_completo')),
                When(total_pago_calculado__gt=0, then=Value('parcialmente_pago')),
                default=Value('nao_pago'),
                output_field=models.CharField()
            )
        )
    
    def ativas(self):
        """Vendas que não foram canceladas ou concluídas"""
        return self.filter(
            status__in=['rascunho', 'orcamento', 'aguardando_pagamento', 'parcialmente_pago', 'pago', 'confirmada']
        )
    
    def por_status(self, status):
        """Filtro por status específico"""
        return self.filter(status=status)
    
    def do_mes_atual(self):
        """Vendas do mês atual"""
        hoje = timezone.now()
        return self.filter(
            data_venda__year=hoje.year,
            data_venda__month=hoje.month
        )
    
    def do_vendedor(self, vendedor):
        """Vendas de um vendedor específico"""
        return self.filter(vendedor=vendedor)
    
    def com_pagamento_pendente(self):
        """Vendas que ainda têm valores pendentes"""
        return self.com_totais_calculados().filter(
            total_pendente_calculado__gt=0
        )
    
    def dashboard_resumo(self):
        """
        Dados resumidos para dashboard
        Query otimizada para estatísticas gerais
        """
        return self.aggregate(
            total_vendas=Count('id'),
            total_valor=Sum('valor_total'),
            total_pago=Sum('pagamentos__valor', filter=Q(pagamentos__status='confirmado')),
            total_pendente=Sum('valor_total') - Coalesce(Sum('pagamentos__valor', filter=Q(pagamentos__status='confirmado')), 0),
            
            # Por status
            vendas_rascunho=Count('id', filter=Q(status='rascunho')),
            vendas_confirmadas=Count('id', filter=Q(status='confirmada')),
            vendas_canceladas=Count('id', filter=Q(status='cancelada')),
        )
    
    def por_periodo(self, data_inicio, data_fim):
        """Vendas em um período específico"""
        return self.filter(
            data_venda__date__range=[data_inicio, data_fim]
        )
    
    def buscar(self, termo):
        """
        Busca por código, cliente ou observações
        """
        if not termo:
            return self.all()
            
        return self.com_dados_completos().filter(
            Q(codigo__icontains=termo) |
            Q(cliente__nome__icontains=termo) |
            Q(cliente__documento__icontains=termo) |
            Q(observacoes__icontains=termo) |
            Q(bloqueio__nome__icontains=termo) |
            Q(bloqueio__descricao__icontains=termo)
        ).distinct()
    
    def para_relatorio_vendas(self):
        """
        Query específica para relatórios de vendas
        Inclui todos os dados necessários de uma vez
        """
        return self.com_totais_calculados().select_related(
            'bloqueio__caravana',
        ).order_by('-data_venda')
    
    def vencendo_hoje(self):
        """
        Vendas com viagem hoje (para notificações)
        """
        hoje = timezone.now().date()
        return self.filter(
            bloqueio__saida=hoje,
            status__in=['confirmada', 'pago']
        )
    
    def vencendo_em_breve(self, dias=7):
        """
        Vendas com viagem nos próximos X dias
        """
        hoje = timezone.now().date()
        data_limite = hoje + timezone.timedelta(days=dias)
        
        return self.filter(
            bloqueio__saida__range=[hoje, data_limite],
            status__in=['confirmada', 'pago']
        )