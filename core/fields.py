# -*- coding: utf-8 -*-
from django.db import models
from .utils.encryption import field_encryption


class EncryptedCharField(models.CharField):
    """
    Campo CharField que criptografa automaticamente o valor antes de salvar
    e descriptografa ao recuperar do banco de dados.
    """
    
    def __init__(self, *args, **kwargs):
        # Remove o atributo show_in_admin personalizado se presente
        self.show_encrypted_in_admin = kwargs.pop('show_encrypted_in_admin', False)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """
        Descriptografa o valor ao recuperar do banco
        """
        if value is None:
            return value
        return field_encryption.decrypt(value)
    
    def to_python(self, value):
        """
        Converte o valor para Python (usado em formulários)
        """
        if value is None:
            return value
        
        # Se já é uma string descriptografada, retorna ela
        if isinstance(value, str):
            # Tenta descriptografar, se falhar retorna o valor original
            try:
                return field_encryption.decrypt(value)
            except:
                return value
        
        return str(value)
    
    def get_prep_value(self, value):
        """
        Criptografa o valor antes de salvar no banco
        """
        if value is None:
            return value
        
        # Só criptografa se não estiver já criptografado
        if isinstance(value, str) and value:
            return field_encryption.encrypt(value)
        
        return value


class EncryptedTextField(models.TextField):
    """
    Campo TextField que criptografa automaticamente o valor antes de salvar
    e descriptografa ao recuperar do banco de dados.
    """
    
    def __init__(self, *args, **kwargs):
        self.show_encrypted_in_admin = kwargs.pop('show_encrypted_in_admin', False)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """
        Descriptografa o valor ao recuperar do banco
        """
        if value is None:
            return value
        return field_encryption.decrypt(value)
    
    def to_python(self, value):
        """
        Converte o valor para Python (usado em formulários)
        """
        if value is None:
            return value
        
        if isinstance(value, str):
            try:
                return field_encryption.decrypt(value)
            except:
                return value
        
        return str(value)
    
    def get_prep_value(self, value):
        """
        Criptografa o valor antes de salvar no banco
        """
        if value is None:
            return value
        
        if isinstance(value, str) and value:
            return field_encryption.encrypt(value)
        
        return value