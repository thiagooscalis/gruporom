# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div
from core.models import Caravana, Pessoa, Bloqueio
from core.choices import MOEDA_CHOICES


class CaravanaForm(forms.ModelForm):
    """
    Formulário para criar/editar caravanas com campos dos bloqueios
    """
    
    # Campo para autocomplete do responsável
    responsavel_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do responsável para buscar...'
        }),
        label="Buscar Responsável"
    )
    
    # Campo URL customizado para evitar warnings
    link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control', 
            'placeholder': 'https://'
        }),
        assume_scheme='https'
    )
    
    # Campos dos bloqueios que serão criados automaticamente
    data_saida = forms.DateField(
        label="Data de Saída",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Data de saída para todos os bloqueios"
    )
    valor_economica = forms.DecimalField(
        label="Valor Econômica",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        help_text="Valor do bloqueio Econômica"
    )
    valor_executiva = forms.DecimalField(
        label="Valor Executiva", 
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        help_text="Valor do bloqueio Executiva"
    )
    valor_terrestre = forms.DecimalField(
        label="Valor Terrestre",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        help_text="Valor do bloqueio Terrestre"
    )
    taxas = forms.DecimalField(
        label="Taxas",
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        help_text="Taxas aplicadas a todos os bloqueios"
    )
    moeda_valor = forms.ChoiceField(
        label="Moeda dos Valores",
        choices=MOEDA_CHOICES,
        initial='Dólar'
    )
    moeda_taxas = forms.ChoiceField(
        label="Moeda das Taxas", 
        choices=MOEDA_CHOICES,
        initial='Dólar'
    )
    
    class Meta:
        model = Caravana
        fields = [
            'nome',
            'empresa',
            'tipo',
            'promotor',
            'responsavel',
            'lideres',
            'quantidade',
            'free_economica',
            'free_executiva',
            'repasse_valor',
            'repasse_tipo',
            'repasse_moeda',
            'data_contrato',
            'link',
            'destaque_site',
        ]
        widgets = {
            'data_contrato': forms.DateInput(attrs={'type': 'date'}),
            'lideres': forms.SelectMultiple(attrs={'size': '5'}),
            'quantidade': forms.NumberInput(attrs={'min': '1'}),
            'free_economica': forms.NumberInput(attrs={'min': '0'}),
            'free_executiva': forms.NumberInput(attrs={'min': '0'}),
            'repasse_valor': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'destaque_site': forms.NumberInput(attrs={'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas pessoas ativas para líderes e promotor
        pessoas_ativas = Pessoa.objects.filter(
            usuario__is_active=True
        ).distinct()
        
        self.fields['promotor'].queryset = pessoas_ativas
        self.fields['lideres'].queryset = pessoas_ativas
        
        # Responsável pode ser qualquer pessoa ou empresa (quem está fechando o negócio)
        self.fields['responsavel'].queryset = Pessoa.objects.all()
        self.fields['responsavel'].widget = forms.HiddenInput()  # Será substituído por autocomplete
        
        # Remove o widget padrão do campo lideres - será substituído por autocomplete
        self.fields['lideres'].widget = forms.MultipleHiddenInput()
        
        # Filtra apenas empresas de turismo
        empresas_validas = Pessoa.objects.filter(
            tipo_empresa='Turismo',
            tipo_doc='CNPJ'  # Empresas devem ter CNPJ
        )
        
        # Se o usuário tem empresas associadas, cruza com empresas válidas
        if self.user and hasattr(self.user, 'empresas'):
            empresas_usuario = self.user.empresas.all()
            if empresas_usuario.exists():
                # Intersecção: empresas do usuário que são válidas
                empresas_validas = empresas_validas.filter(
                    id__in=empresas_usuario.values_list('id', flat=True)
                )
        
        self.fields['empresa'].queryset = empresas_validas
        
        # Configuração do Crispy Forms (simplificado pois estamos usando renderização manual)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_show_labels = True
        self.helper.form_show_errors = True
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Valida que free não excede a quantidade total
        quantidade = cleaned_data.get('quantidade', 0)
        free_economica = cleaned_data.get('free_economica', 0)
        free_executiva = cleaned_data.get('free_executiva', 0)
        
        if free_economica + free_executiva > quantidade:
            raise forms.ValidationError({
                'quantidade': 'A soma dos passageiros free não pode exceder a quantidade total'
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        # Verifica se é uma nova caravana antes de salvar
        is_new = self.instance.pk is None
        
        caravana = super().save(commit=commit)
        
        # Só cria os bloqueios se for uma nova caravana (não edição)
        if commit and is_new:
            data_saida = self.cleaned_data.get('data_saida')
            valor_economica = self.cleaned_data.get('valor_economica')
            valor_executiva = self.cleaned_data.get('valor_executiva')
            valor_terrestre = self.cleaned_data.get('valor_terrestre')
            taxas = self.cleaned_data.get('taxas')
            moeda_valor = self.cleaned_data.get('moeda_valor')
            moeda_taxas = self.cleaned_data.get('moeda_taxas')
            
            # Criar Bloqueio Econômica
            Bloqueio.objects.create(
                caravana=caravana,
                descricao="Econômica",
                saida=data_saida,
                valor=valor_economica,
                taxas=taxas,
                moeda_valor=moeda_valor,
                moeda_taxas=moeda_taxas,
                terrestre=False,
                ativo=True
            )
            
            # Criar Bloqueio Executiva  
            Bloqueio.objects.create(
                caravana=caravana,
                descricao="Executiva",
                saida=data_saida,
                valor=valor_executiva,
                taxas=taxas,
                moeda_valor=moeda_valor,
                moeda_taxas=moeda_taxas,
                terrestre=False,
                ativo=True
            )
            
            # Criar Bloqueio Terrestre
            Bloqueio.objects.create(
                caravana=caravana,
                descricao="Terrestre",
                saida=data_saida,
                valor=valor_terrestre,
                taxas=taxas,
                moeda_valor=moeda_valor,
                moeda_taxas=moeda_taxas,
                terrestre=True,
                ativo=True
            )
        
        return caravana