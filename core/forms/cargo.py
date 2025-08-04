# -*- coding: utf-8 -*-
from django import forms
from core.models import Cargo, Pessoa


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'empresa', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do cargo...'
            }),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Cargo',
            'empresa': 'Empresa',
            'ativo': 'Cargo Ativo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra apenas empresas do Grupo ROM
        self.fields['empresa'].queryset = Pessoa.objects.filter(
            empresa_gruporom=True
        ).order_by('nome')
        
        # Define empty label
        self.fields['empresa'].empty_label = "Selecione uma empresa"
        
        # Se for novo cargo, ativo vem marcado por padrão
        if not self.instance.pk:
            self.initial['ativo'] = True