# -*- coding: utf-8 -*-
from django import forms
from django.forms import inlineformset_factory
from core.models import Pessoa, Telefone, Email


class TelefoneForm(forms.ModelForm):
    """
    Formulário para telefones
    """
    
    class Meta:
        model = Telefone
        fields = ['ddi', 'ddd', 'telefone', 'tipo', 'principal']
        widgets = {
            'ddi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DDI',
                'maxlength': '4',
                'value': '55'
            }),
            'ddd': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DDD',
                'maxlength': '3'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control telefone-mask',
                'placeholder': 'Telefone',
                'maxlength': '15'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'ddi': 'DDI',
            'ddd': 'DDD',
            'telefone': 'Telefone',
            'tipo': 'Tipo',
            'principal': 'Principal'
        }


class EmailForm(forms.ModelForm):
    """
    Formulário para emails
    """
    
    class Meta:
        model = Email
        fields = ['email', 'tipo', 'principal']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'email': 'E-mail',
            'tipo': 'Tipo',
            'principal': 'Principal'
        }


# Formsets inline para telefones e emails
TelefoneFormSet = inlineformset_factory(
    Pessoa, 
    Telefone, 
    form=TelefoneForm,
    extra=1,  # Quantos formulários extras exibir
    min_num=1,  # Mínimo de 1 telefone
    validate_min=True,
    can_delete=True
)

EmailFormSet = inlineformset_factory(
    Pessoa,
    Email,
    form=EmailForm,
    extra=1,  # Quantos formulários extras exibir
    min_num=1,  # Mínimo de 1 email
    validate_min=True,
    can_delete=True
)