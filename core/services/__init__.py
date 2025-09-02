# -*- coding: utf-8 -*-
"""
Services Layer - Lógica de negócio centralizada

Este módulo contém os services responsáveis pelas regras de negócio
da aplicação, mantendo as views focadas apenas em apresentação.
"""

from .venda_service import VendaService

__all__ = [
    'VendaService',
]