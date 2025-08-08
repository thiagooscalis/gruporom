# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div
from core.models import Caravana, Pessoa, Bloqueio
from core.choices import MOEDA_CHOICES


class CaravanaForm(forms.ModelForm):
    """
    Formulário para criar/editar caravanas com campos dos bloqueios
    """
    
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
            'lideres',
            'quantidade',
            'free_economica',
            'free_executiva',
            'repasse_valor',
            'repasse_tipo',
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra apenas pessoas ativas para líderes
        pessoas_ativas = Pessoa.objects.filter(
            usuario__is_active=True
        ).distinct()
        
        self.fields['promotor'].queryset = pessoas_ativas
        self.fields['lideres'].queryset = pessoas_ativas
        
        # Remove o widget padrão do campo lideres - será substituído por autocomplete
        self.fields['lideres'].widget = forms.MultipleHiddenInput()
        
        # Se o usuário tem empresas associadas, filtra
        if user and hasattr(user, 'empresas'):
            empresas_usuario = user.empresas.all()
            if empresas_usuario.exists():
                self.fields['empresa'].queryset = empresas_usuario
        
        # Configuração do Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3"><i class="fas fa-info-circle me-2"></i>Informações da Caravana</h5>'),
            Row(
                Column('nome', css_class='col-md-6'),
                Column('empresa', css_class='col-md-3'),
                Column('tipo', css_class='col-md-3'),
            ),
            Row(
                Column('promotor', css_class='col-md-6'),
                Column('data_contrato', css_class='col-md-6'),
            ),
            Row(
                Column('quantidade', css_class='col-md-4'),
                Column('free_economica', css_class='col-md-4'),
                Column('free_executiva', css_class='col-md-4'),
            ),
            Row(
                Column('repasse_valor', css_class='col-md-6'),
                Column('repasse_tipo', css_class='col-md-6'),
            ),
            HTML('<div class="col-md-12" id="lideres-autocomplete-container"></div>'),
            Row(
                Column('link', css_class='col-md-9'),
                Column('destaque_site', css_class='col-md-3'),
            ),
            
            HTML('<hr class="my-4">'),
            HTML('<h5 class="mb-3"><i class="fas fa-calendar-alt me-2"></i>Dados dos Bloqueios</h5>'),
            HTML('<p class="text-muted mb-3">Serão criados automaticamente 3 bloqueios: Econômica, Executiva e Terrestre</p>'),
            
            Row(
                Column('data_saida', css_class='col-md-6'),
                Column('taxas', css_class='col-md-6'),
            ),
            Row(
                Column('moeda_valor', css_class='col-md-6'),
                Column('moeda_taxas', css_class='col-md-6'),
            ),
            Row(
                Column('valor_economica', css_class='col-md-4'),
                Column('valor_executiva', css_class='col-md-4'),
                Column('valor_terrestre', css_class='col-md-4'),
            ),
        )
    
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