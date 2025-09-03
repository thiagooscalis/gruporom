# -*- coding: utf-8 -*-
"""
VendaService - Lógica de negócio para vendas de bloqueios

Este service centraliza todas as regras de negócio relacionadas a vendas,
mantendo as views focadas apenas em apresentação.
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from typing import Dict, List, Optional

from core.models import (
    VendaBloqueio, Bloqueio, Pessoa, Passageiro, 
    ExtraVenda, Extra, Pagamento, Cambio
)
from .exceptions import (
    VendaError, PassageirosIndisponiveisError, 
    VendaNaoEditavelError, PagamentoError, ValorPagamentoInvalidoError
)


class VendaService:
    """
    Service para gerenciar vendas de bloqueios
    Centraliza todas as regras de negócio
    """
    
    @transaction.atomic
    def criar_venda_bloqueio(self, dados_venda: Dict) -> VendaBloqueio:
        """
        Cria uma nova venda de bloqueio com todas as validações
        
        Args:
            dados_venda: Dict com os dados da venda
                - bloqueio_id: ID do bloqueio
                - cliente_id: ID do cliente
                - vendedor: Usuario vendedor
                - quantidade: Número de passageiros
                - observacoes: Observações opcionais
                
        Returns:
            VendaBloqueio: Venda criada
            
        Raises:
            VendaError: Se houver erro nas regras de negócio
        """
        # 1. Validar disponibilidade
        bloqueio = self._get_bloqueio(dados_venda['bloqueio_id'])
        quantidade = dados_venda['quantidade']
        
        self._validar_disponibilidade_passageiros(bloqueio, quantidade)
        
        # 2. Calcular valores
        valores = self._calcular_valores_venda(bloqueio, quantidade)
        
        # 3. Criar venda
        venda = VendaBloqueio.objects.create(
            bloqueio=bloqueio,
            cliente_id=dados_venda['cliente_id'],
            vendedor=dados_venda['vendedor'],
            status='pre-venda',
            data_venda=timezone.now(),
            numero_passageiros=quantidade,
            valor_passageiros=valores['valor_passageiros'],
            valor_total=valores['valor_total'],
            valor_pendente=valores['valor_total'],
            observacoes=dados_venda.get('observacoes', ''),
        )
        
        # 4. Log da atividade (opcional)
        self._log_atividade_venda(venda, 'Venda criada', dados_venda['vendedor'])
        
        return venda
    
    def adicionar_passageiro_venda(self, venda_id: int, pessoa_id: int, 
                                   valor_individual: Optional[Decimal] = None) -> Passageiro:
        """
        Adiciona um passageiro à venda
        
        Args:
            venda_id: ID da venda
            pessoa_id: ID da pessoa
            valor_individual: Valor específico (opcional)
            
        Returns:
            Passageiro: Passageiro criado
            
        Raises:
            VendaError: Se a venda não permitir alterações
        """
        venda = self._get_venda_editavel(venda_id)
        
        # Verificar se já não existe esse passageiro na venda
        if Passageiro.objects.filter(venda=venda, pessoa_id=pessoa_id).exists():
            raise VendaError(f"Pessoa já está cadastrada como passageiro desta venda")
        
        # Calcular valor se não fornecido
        if valor_individual is None:
            valor_individual = self._calcular_valor_por_passageiro(venda.bloqueio)
        
        # Criar passageiro
        passageiro = Passageiro.objects.create(
            pessoa_id=pessoa_id,
            bloqueio=venda.bloqueio,
            venda=venda
        )
        
        # Recalcular totais da venda
        self._recalcular_totais_venda(venda)
        
        return passageiro
    
    def registrar_pagamento(self, venda_id: int, dados_pagamento: Dict) -> Pagamento:
        """
        Registra um pagamento para a venda
        
        Args:
            venda_id: ID da venda
            dados_pagamento: Dict com dados do pagamento
                - valor: Valor do pagamento
                - forma_pagamento: Forma de pagamento
                - referencia: Referência/comprovante (opcional)
                - observacoes: Observações (opcional)
                
        Returns:
            Pagamento: Pagamento criado
            
        Raises:
            PagamentoError: Se houver erro no pagamento
        """
        venda = VendaBloqueio.objects.get(id=venda_id)
        valor_pagamento = Decimal(str(dados_pagamento['valor']))
        
        # Validar valor
        if valor_pagamento <= 0:
            raise PagamentoError("Valor do pagamento deve ser positivo")
        
        if valor_pagamento > venda.valor_pendente:
            raise ValorPagamentoInvalidoError(valor_pagamento, venda.valor_pendente)
        
        # Criar pagamento
        pagamento = Pagamento.objects.create(
            venda=venda,
            valor=valor_pagamento,
            forma_pagamento=dados_pagamento['forma_pagamento'],
            status='confirmado',  # Por padrão confirmado
            data_pagamento=timezone.now(),
            data_confirmacao=timezone.now(),
            referencia=dados_pagamento.get('referencia', ''),
            observacoes=dados_pagamento.get('observacoes', ''),
        )
        
        # Recalcular totais (feito automaticamente no save do pagamento)
        # mas vamos forçar para garantir
        self._recalcular_totais_venda(venda)
        
        return pagamento
    
    def cancelar_venda(self, venda_id: int, motivo: str, usuario) -> VendaBloqueio:
        """
        Cancela uma venda
        
        Args:
            venda_id: ID da venda
            motivo: Motivo do cancelamento
            usuario: Usuário que está cancelando
            
        Returns:
            VendaBloqueio: Venda cancelada
            
        Raises:
            VendaError: Se não puder cancelar
        """
        venda = VendaBloqueio.objects.get(id=venda_id)
        
        if not venda.pode_cancelar:
            raise VendaError(f"Venda com status '{venda.status}' não pode ser cancelada")
        
        # Verificar se tem pagamentos confirmados
        pagamentos_confirmados = venda.pagamentos.filter(status='confirmado')
        if pagamentos_confirmados.exists():
            # TODO: Implementar estorno de pagamentos se necessário
            pass
        
        # Cancelar venda
        venda.status = 'cancelada'
        venda.data_cancelamento = timezone.now()
        venda.motivo_cancelamento = motivo
        venda.save()
        
        # Liberar passageiros (remover vinculo com venda)
        venda.passageiros.update(venda=None)
        
        self._log_atividade_venda(venda, f'Venda cancelada: {motivo}', usuario)
        
        return venda
    
    def confirmar_venda(self, venda_id: int, usuario) -> VendaBloqueio:
        """
        Confirma uma venda (após pagamento completo)
        
        Args:
            venda_id: ID da venda
            usuario: Usuário confirmando
            
        Returns:
            VendaBloqueio: Venda confirmada
        """
        venda = VendaBloqueio.objects.get(id=venda_id)
        
        if not venda.pode_confirmar:
            raise VendaError("Venda não pode ser confirmada. Verifique o status e pagamentos.")
        
        venda.status = 'confirmada'
        venda.data_confirmacao = timezone.now()
        venda.save()
        
        self._log_atividade_venda(venda, 'Venda confirmada', usuario)
        
        return venda
    
    def listar_vendas_usuario(self, usuario, filtros: Optional[Dict] = None):
        """
        Lista vendas do usuário com filtros opcionais
        
        Args:
            usuario: Usuario
            filtros: Filtros opcionais (status, periodo, etc.)
            
        Returns:
            QuerySet: Vendas filtradas com dados otimizados
        """
        queryset = VendaBloqueio.objects.com_totais_calculados()
        
        # Filtrar por vendedor se não for admin
        if not usuario.is_superuser:
            queryset = queryset.filter(vendedor=usuario)
        
        # Aplicar filtros
        if filtros:
            if 'status' in filtros and filtros['status']:
                status = filtros['status']
                if isinstance(status, list):
                    queryset = queryset.filter(status__in=status)
                else:
                    queryset = queryset.filter(status=status)
            
            if 'data_inicio' in filtros and filtros['data_inicio']:
                queryset = queryset.filter(data_venda__date__gte=filtros['data_inicio'])
            
            if 'data_fim' in filtros and filtros['data_fim']:
                queryset = queryset.filter(data_venda__date__lte=filtros['data_fim'])
                
            if 'busca' in filtros and filtros['busca']:
                termo = filtros['busca']
                queryset = queryset.filter(
                    Q(codigo__icontains=termo) |
                    Q(cliente__nome__icontains=termo) |
                    Q(cliente__cpf__icontains=termo) |
                    Q(cliente__cnpj__icontains=termo) |
                    Q(observacoes__icontains=termo)
                )
        
        return queryset.order_by('-data_venda')
    
    def obter_dashboard_vendas(self, usuario) -> Dict:
        """
        Obtém dados para dashboard de vendas
        
        Args:
            usuario: Usuario
            
        Returns:
            Dict: Dados do dashboard
        """
        # Base query
        vendas_base = VendaBloqueio.objects.all()
        if not usuario.is_superuser:
            vendas_base = vendas_base.filter(vendedor=usuario)
        
        # Estatísticas gerais - usando aggregate diretamente
        from django.db.models import Count, Sum
        resumo_geral = vendas_base.aggregate(
            total_vendas=Count('id'),
            total_valor=Sum('valor_total'),
            vendas_pre_venda=Count('id', filter=Q(status='pre-venda')),
            vendas_confirmadas=Count('id', filter=Q(status='confirmada')),
        )
        
        # Vendas do mês atual
        hoje = timezone.now()
        vendas_mes = vendas_base.filter(
            data_venda__year=hoje.year,
            data_venda__month=hoje.month
        )[:10]
        
        # Vendas com pagamento pendente
        pendentes = vendas_base.filter(valor_pendente__gt=0)[:5]
        
        # Viagens próximas
        data_limite = hoje.date() + timezone.timedelta(days=7)
        viagens_proximas = vendas_base.filter(
            bloqueio__saida__range=[hoje.date(), data_limite],
            status__in=['confirmada', 'concluida']
        )[:5]
        
        return {
            'resumo_geral': resumo_geral,
            'vendas_mes': vendas_mes,
            'vendas_pendentes': pendentes,
            'viagens_proximas': viagens_proximas,
            'total_vendas_usuario': vendas_base.count(),
        }
    
    # Métodos privados auxiliares
    
    def _get_bloqueio(self, bloqueio_id: int) -> Bloqueio:
        """Busca bloqueio ou levanta exceção"""
        try:
            return Bloqueio.objects.select_related('caravana').get(id=bloqueio_id)
        except Bloqueio.DoesNotExist:
            raise VendaError(f"Bloqueio {bloqueio_id} não encontrado")
    
    def _get_venda_editavel(self, venda_id: int) -> VendaBloqueio:
        """Busca venda editável ou levanta exceção"""
        try:
            venda = VendaBloqueio.objects.get(id=venda_id)
            if not venda.pode_editar:
                raise VendaNaoEditavelError(venda.status)
            return venda
        except VendaBloqueio.DoesNotExist:
            raise VendaError(f"Venda {venda_id} não encontrada")
    
    def _validar_disponibilidade_passageiros(self, bloqueio: Bloqueio, quantidade: int):
        """Valida se há passageiros disponíveis"""
        # Contar passageiros já vendidos
        vendidos = Passageiro.objects.filter(
            bloqueio=bloqueio,
            venda__isnull=False,
            venda__status__in=['confirmada', 'concluida']
        ).count()
        
        disponiveis = bloqueio.caravana.quantidade - vendidos
        
        if quantidade > disponiveis:
            raise PassageirosIndisponiveisError(quantidade, disponiveis)
    
    def _calcular_valores_venda(self, bloqueio: Bloqueio, quantidade: int) -> Dict:
        """Calcula valores da venda"""
        valor_por_passageiro = self._calcular_valor_por_passageiro(bloqueio)
        valor_total = valor_por_passageiro * quantidade
        
        return {
            'valor_por_passageiro': valor_por_passageiro,
            'valor_passageiros': valor_total,
            'valor_total': valor_total,
        }
    
    def _calcular_valor_por_passageiro(self, bloqueio: Bloqueio) -> Decimal:
        """Calcula valor por passageiro com conversão de moeda se necessário"""
        valor_base = bloqueio.valor + bloqueio.taxas
        
        # TODO: Implementar conversão USD/BRL se necessário
        # Por enquanto assumindo que já está em BRL
        return Decimal(str(valor_base))
    
    def _recalcular_totais_venda(self, venda: VendaBloqueio):
        """Recalcula todos os totais da venda"""
        venda.calcular_totais()
        venda.save(update_fields=[
            'valor_passageiros', 'valor_extras', 'valor_total', 
            'valor_pago', 'valor_pendente', 'numero_passageiros', 'status'
        ])
    
    def _log_atividade_venda(self, venda: VendaBloqueio, atividade: str, usuario):
        """Log de atividades da venda (opcional - para auditoria)"""
        # TODO: Implementar sistema de log/auditoria se necessário
        pass