# -*- coding: utf-8 -*-
"""
Exceções customizadas para regras de negócio

Estas exceções representam violações de regras de negócio
e devem ser capturadas pelas views para exibir mensagens apropriadas.
"""


class BusinessError(Exception):
    """Exceção base para erros de regras de negócio"""
    
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code


class VendaError(BusinessError):
    """Exceções relacionadas a vendas"""
    pass


class PassageirosIndisponiveisError(VendaError):
    """Não há passageiros suficientes disponíveis"""
    
    def __init__(self, solicitados, disponiveis):
        message = f"Solicitados {solicitados} passageiros, apenas {disponiveis} disponíveis"
        super().__init__(message, code='passageiros_indisponiveis')
        self.solicitados = solicitados
        self.disponiveis = disponiveis


class VendaNaoEditavelError(VendaError):
    """Venda não pode ser editada no status atual"""
    
    def __init__(self, status):
        message = f"Venda com status '{status}' não pode ser editada"
        super().__init__(message, code='venda_nao_editavel')
        self.status = status


class PagamentoError(BusinessError):
    """Exceções relacionadas a pagamentos"""
    pass


class ValorPagamentoInvalidoError(PagamentoError):
    """Valor do pagamento é inválido"""
    
    def __init__(self, valor_pagamento, valor_pendente):
        message = f"Pagamento R$ {valor_pagamento} excede valor pendente R$ {valor_pendente}"
        super().__init__(message, code='valor_pagamento_invalido')
        self.valor_pagamento = valor_pagamento
        self.valor_pendente = valor_pendente


class ClienteError(BusinessError):
    """Exceções relacionadas a clientes"""
    pass