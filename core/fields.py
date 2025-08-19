# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
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


class AutocompleteField(forms.ModelChoiceField):
    """
    Campo customizado para autocomplete usando Alpine.js + Tailwind CSS
    
    Combina um campo hidden para o ID com um campo de busca visível
    e fornece uma interface moderna de autocomplete.
    """
    
    def __init__(self, queryset, search_url=None, search_placeholder="Digite para buscar...", 
                 selected_label="Item selecionado:", min_length=2, **kwargs):
        
        self.search_url = search_url
        self.search_placeholder = search_placeholder
        self.selected_label = selected_label
        self.min_length = min_length
        
        # Importar widget localmente para evitar circular import
        from .widgets import AutocompleteWidget
        
        # Usar widget customizado
        kwargs['widget'] = AutocompleteWidget(
            search_url=search_url,
            search_placeholder=search_placeholder,
            selected_label=selected_label,
            min_length=min_length
        )
        
        super().__init__(queryset, **kwargs)
    
    def prepare_value(self, value):
        """Prepara valor para o widget"""
        if value is None:
            return None
        
        # Se value é um modelo, retorna o ID
        if hasattr(value, 'pk'):
            return value.pk
        
        # Se value é já um ID
        return value
    
    def to_python(self, value):
        """Converte valor para o modelo Python"""
        if value in self.empty_values:
            return None
        
        try:
            key = self.to_field_name or 'pk'
            if isinstance(value, self.queryset.model):
                value = getattr(value, key)
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice'
            )
        return value