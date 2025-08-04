# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field
from core.models import Colaborador, Pessoa, Cargo, Turno


class ColaboradorForm(forms.ModelForm):
    """Form para criação e edição de colaboradores"""
    
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.none(),  # Vazio por padrão
        required=True,
        widget=forms.HiddenInput(),
        label="Pessoa"
    )
    
    pessoa_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome, documento ou email da pessoa...',
            'autocomplete': 'off'
        }),
        label="Buscar Pessoa"
    )
    
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.filter(ativo=True).select_related('empresa'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Cargo",
        empty_label="Selecione um cargo..."
    )
    
    turnos = forms.ModelMultipleChoiceField(
        queryset=Turno.objects.filter(ativo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Turnos Disponíveis"
    )
    
    class Meta:
        model = Colaborador
        fields = [
            'pessoa', 'cargo', 'salario', 'data_admissao', 'data_demissao',
            'gorjeta', 'comissao', 'turnos', 'ativo'
        ]
        widgets = {
            'salario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'data_admissao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_demissao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'comissao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'gorjeta': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se for edição, pré-preenche o campo de busca e pessoa selecionada
        if self.instance.pk:
            self.fields['pessoa'].queryset = Pessoa.objects.filter(pk=self.instance.pessoa.pk)
            self.fields['pessoa_search'].initial = f"{self.instance.pessoa.nome} - {self.instance.pessoa.doc}"
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('pessoa_search', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Field('pessoa'),
            Row(
                Column('cargo', css_class='form-group col-md-6 mb-0'),
                Column('salario', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('data_admissao', css_class='form-group col-md-6 mb-0'),
                Column('data_demissao', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('comissao', css_class='form-group col-md-6 mb-0'),
                Column(
                    Field('gorjeta', css_class='form-check-input'),
                    css_class='form-group col-md-3 mb-0'
                ),
                Column(
                    Field('ativo', css_class='form-check-input'),
                    css_class='form-group col-md-3 mb-0'
                ),
                css_class='form-row'
            ),
            'turnos'
        )
    
    def clean_pessoa(self):
        """Valida o campo pessoa"""
        pessoa_id = self.data.get('pessoa')
        if pessoa_id:
            try:
                pessoa = Pessoa.objects.get(pk=pessoa_id)
                # Verifica se a pessoa já é colaborador (exceto no caso de edição)
                if hasattr(pessoa, 'colaborador') and (not self.instance.pk or pessoa.colaborador.pk != self.instance.pk):
                    raise forms.ValidationError("Esta pessoa já é um colaborador.")
                return pessoa
            except Pessoa.DoesNotExist:
                raise forms.ValidationError("Pessoa inválida.")
        
        raise forms.ValidationError("Selecione uma pessoa válida.")
    
    def save(self, commit=True):
        colaborador = super().save(commit=False)
        
        if commit:
            colaborador.save()
            # Salva os turnos (M2M)
            self.save_m2m()
        
        return colaborador