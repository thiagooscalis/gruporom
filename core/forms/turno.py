# -*- coding: utf-8 -*-
from django import forms
from core.models import Turno


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['nome', 'inicio', 'fim', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do turno...'
            }),
            'inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'fim': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Turno',
            'inicio': 'Horário de Início',
            'fim': 'Horário de Fim',
            'ativo': 'Turno Ativo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se for novo turno, ativo vem marcado por padrão
        if not self.instance.pk:
            self.initial['ativo'] = True