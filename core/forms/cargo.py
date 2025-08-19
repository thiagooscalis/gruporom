# -*- coding: utf-8 -*-
from django import forms
from core.models import Cargo, Pessoa


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['nome', 'empresa', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Digite o nome do cargo...'
            }),
            'empresa': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-slate-300 rounded'
            }),
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