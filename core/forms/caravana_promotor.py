# -*- coding: utf-8 -*-
from django import forms
from core.models import Caravana, Pessoa, Pais, Aeroporto
from core.choices import TIPO_CARAVANA_CHOICES, REPASSE_TIPO_CHOICES
from core.form_fields import PaisesMultiSelectField, PessoasMultiSelectField, AeroportoField


class CaravanaPromotorForm(forms.ModelForm):
    """
    Formulário multistep para cadastro de caravana pelo Promotor
    """
    
    # Step 1 - Dados da Caravana
    data_saida = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data de Saída',
        required=True
    )
    paises = PaisesMultiSelectField(
        queryset=Pais.objects.all().order_by('nome'),
        label='Países do Roteiro',
        required=True
    )
    aeroporto_embarque = AeroportoField(
        queryset=Aeroporto.objects.select_related('cidade__pais').order_by('nome'),
        label='Aeroporto de Embarque',
        required=True
    )
    
    # Step 2 - Líderes (serão adicionados dinamicamente via JavaScript)
    # Os campos de líderes serão tratados manualmente no template
    
    # Step 3 - Responsável (será criado/buscado dinamicamente)
    responsavel_doc = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'data-mask': 'doc'}),
        label='Documento do Responsável',
        required=True
    )
    responsavel_nome = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nome do Responsável',
        required=True
    )
    responsavel_celular = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'data-mask': 'phone'}),
        label='Celular do Responsável',
        required=True
    )
    responsavel_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='E-mail do Responsável',
        required=True
    )
    
    # Step 4 - Valores e Configurações
    valor = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label='Valor',
        required=True,
        decimal_places=2,
        max_digits=10
    )
    moeda = forms.ChoiceField(
        choices=[('Real', 'Real (BRL)'), ('Dólar', 'Dólar (USD)'), ('Euro', 'Euro (EUR)')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Moeda',
        required=True
    )
    taxas = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label='Taxas',
        required=False,
        decimal_places=2,
        max_digits=10,
        initial=0
    )
    moeda_taxas = forms.ChoiceField(
        choices=[('Real', 'Real (BRL)'), ('Dólar', 'Dólar (USD)'), ('Euro', 'Euro (EUR)')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Moeda das Taxas',
        required=False
    )
    roteiro_pdf = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        label='Roteiro em PDF',
        required=False
    )
    
    # Campo de líderes usando o novo MultiSelectField
    lideres = PessoasMultiSelectField(
        queryset=Pessoa.objects.filter(tipo_doc='CPF').order_by('nome'),
        label='Líderes',
        required=False
    )
    
    class Meta:
        model = Caravana
        fields = [
            'nome', 'empresa', 'tipo', 'lideres', 'quantidade', 
            'free_economica', 'free_executiva', 'data_contrato',
            'repasse_valor', 'repasse_tipo', 'link'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da caravana'}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'free_economica': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'value': '0'}),
            'free_executiva': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'value': '0'}),
            'data_contrato': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'repasse_valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'repasse_tipo': forms.Select(attrs={'class': 'form-select'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://', 'required': False}),
        }
        labels = {
            'free_economica': 'Número de Frees na Econômica',
            'free_executiva': 'Número de Frees na Executiva',
            'repasse_valor': 'Valor do Repasse',
            'repasse_tipo': 'Tipo de Repasse',
            'data_contrato': 'Data do Contrato',
            'quantidade': 'Quantidade de Passageiros',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas empresas do Grupo ROM de turismo
        self.fields['empresa'].queryset = Pessoa.objects.filter(
            empresa_gruporom=True,
            tipo_empresa='Turismo'
        ).order_by('nome')
        
        # Tornar campos obrigatórios
        self.fields['nome'].required = True
        self.fields['empresa'].required = True
        self.fields['tipo'].required = True
        self.fields['quantidade'].required = True
        self.fields['data_contrato'].required = True
        self.fields['repasse_valor'].required = True
        self.fields['repasse_tipo'].required = True
        
        # Link é opcional
        self.fields['link'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Valida que free não excede a quantidade total
        quantidade = cleaned_data.get('quantidade', 0)
        free_economica = cleaned_data.get('free_economica', 0)
        free_executiva = cleaned_data.get('free_executiva', 0)
        
        if free_economica + free_executiva > quantidade:
            raise forms.ValidationError(
                'A soma dos passageiros free não pode exceder a quantidade total de passageiros.'
            )
        
        return cleaned_data