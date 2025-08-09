# -*- coding: utf-8 -*-
"""
Validadores para documentos brasileiros e internacionais
"""
import re
from django.core.exceptions import ValidationError


def limpar_documento(documento):
    """
    Remove pontuação e espaços de um documento
    """
    if not documento:
        return ""
    return re.sub(r'[^\w]', '', str(documento))


def validar_cpf(cpf):
    """
    Valida CPF brasileiro
    """
    cpf = limpar_documento(cpf)
    
    if len(cpf) != 11:
        return False
    
    # CPFs inválidos conhecidos
    if cpf == cpf[0] * 11:
        return False
    
    # Calcular primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Calcular segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2


def validar_cnpj(cnpj):
    """
    Valida CNPJ brasileiro
    """
    cnpj = limpar_documento(cnpj)
    
    if len(cnpj) != 14:
        return False
    
    # CNPJs inválidos conhecidos
    if cnpj == cnpj[0] * 14:
        return False
    
    # Primeiro dígito
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso = peso - 1 if peso > 2 else 9
    
    digito1 = 0 if soma % 11 < 2 else 11 - (soma % 11)
    if int(cnpj[12]) != digito1:
        return False
    
    # Segundo dígito
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso = peso - 1 if peso > 2 else 9
    
    digito2 = 0 if soma % 11 < 2 else 11 - (soma % 11)
    return int(cnpj[13]) == digito2


def validar_passaporte(passaporte):
    """
    Valida formato básico de passaporte
    """
    passaporte = limpar_documento(passaporte)
    
    if len(passaporte) < 6 or len(passaporte) > 12:
        return False
    
    # Deve ter pelo menos uma letra e um número
    tem_letra = any(c.isalpha() for c in passaporte)
    tem_numero = any(c.isdigit() for c in passaporte)
    
    return tem_letra and tem_numero


def validate_documento_pessoa(documento, tipo_doc):
    """
    Validator para campo doc do model Pessoa
    """
    if not documento:
        raise ValidationError("Documento é obrigatório.")
    
    documento_limpo = limpar_documento(documento)
    
    if tipo_doc == 'CPF':
        if not validar_cpf(documento_limpo):
            raise ValidationError("CPF inválido. Verifique os números digitados.")
    elif tipo_doc == 'CNPJ':
        if not validar_cnpj(documento_limpo):
            raise ValidationError("CNPJ inválido. Verifique os números digitados.")
    elif tipo_doc == 'Passaporte':
        if not validar_passaporte(documento_limpo):
            raise ValidationError("Passaporte inválido. Deve ter 6-12 caracteres alfanuméricos.")
    
    return documento_limpo