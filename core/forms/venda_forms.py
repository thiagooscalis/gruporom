# -*- coding: utf-8 -*-
"""
Forms para validação de dados de venda

Estes forms fazem a validação de entrada antes de passar
os dados para os services de negócio.
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from core.models import VendaBloqueio, Pessoa, Bloqueio, Passageiro
from core.choices import FORMA_PAGAMENTO_CHOICES, STATUS_VENDA_CHOICES


class CriarVendaForm(forms.Form):
    """
    Form para criação de nova venda
    """
    bloqueio_id = forms.IntegerField(
        label="Bloqueio",
        widget=forms.HiddenInput()
    )
    
    cliente_id = forms.ModelChoiceField(
        queryset=Pessoa.objects.filter(tipo_doc__in=['CPF', 'Passaporte']),
        label="Cliente",
        empty_label="Selecione o cliente...",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    quantidade = forms.IntegerField(
        min_value=1,
        max_value=50,
        label="Quantidade de Passageiros",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True
        })
    )
    
    observacoes = forms.CharField(
        required=False,
        label="Observações",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações sobre a venda (opcional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Personalizar queryset de clientes se necessário
        self.fields['cliente_id'].queryset = Pessoa.objects.filter(
            tipo_doc__in=['CPF', 'Passaporte']
        ).order_by('nome')
    
    def clean_bloqueio_id(self):
        bloqueio_id = self.cleaned_data['bloqueio_id']
        try:
            bloqueio = Bloqueio.objects.get(id=bloqueio_id)
            return bloqueio_id
        except Bloqueio.DoesNotExist:
            raise ValidationError("Bloqueio selecionado não existe.")
    
    def clean(self):
        cleaned_data = super().clean()
        bloqueio_id = cleaned_data.get('bloqueio_id')
        quantidade = cleaned_data.get('quantidade')
        
        if bloqueio_id and quantidade:
            # Validar disponibilidade básica
            try:
                bloqueio = Bloqueio.objects.get(id=bloqueio_id)
                vendidos = Passageiro.objects.filter(
                    bloqueio=bloqueio,
                    venda__isnull=False,
                    venda__status__in=['confirmada', 'pago', 'parcialmente_pago', 'aguardando_pagamento']
                ).count()
                
                disponiveis = bloqueio.caravana.quantidade - vendidos
                
                if quantidade > disponiveis:
                    raise ValidationError(
                        f"Quantidade solicitada ({quantidade}) maior que disponível ({disponiveis})."
                    )
            except Bloqueio.DoesNotExist:
                pass  # Já validado em clean_bloqueio_id
        
        return cleaned_data
    
    def to_service_data(self, user):
        """Converte dados do form para o formato esperado pelo service"""
        return {
            'bloqueio_id': self.cleaned_data['bloqueio_id'],
            'cliente_id': self.cleaned_data['cliente_id'].id,
            'vendedor': user,
            'quantidade': self.cleaned_data['quantidade'],
            'observacoes': self.cleaned_data.get('observacoes', ''),
        }


class AdicionarPassageiroForm(forms.Form):
    """
    Form para adicionar passageiro à venda
    """
    pessoa_id = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        label="Passageiro",
        empty_label="Selecione a pessoa...",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    tipo = forms.ChoiceField(
        choices=[('', 'Normal')] + [
            ('Guia', 'Guia'),
            ('VIP', 'VIP'),
            ('Free', 'Free'),
        ],
        required=False,
        label="Tipo",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    single = forms.BooleanField(
        required=False,
        label="Quarto Single",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def __init__(self, venda, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.venda = venda
        
        # Excluir pessoas já cadastradas nesta venda
        passageiros_existentes = self.venda.passageiros.values_list('pessoa_id', flat=True)
        self.fields['pessoa_id'].queryset = Pessoa.objects.exclude(
            id__in=passageiros_existentes
        ).order_by('nome')
    
    def clean_pessoa_id(self):
        pessoa = self.cleaned_data['pessoa_id']
        
        # Verificar se pessoa já não está cadastrada
        if Passageiro.objects.filter(venda=self.venda, pessoa=pessoa).exists():
            raise ValidationError("Esta pessoa já está cadastrada como passageiro.")
        
        return pessoa


class RegistrarPagamentoForm(forms.Form):
    """
    Form para registrar pagamento
    """
    valor = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        label="Valor",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0,00'
        })
    )
    
    forma_pagamento = forms.ChoiceField(
        choices=FORMA_PAGAMENTO_CHOICES,
        label="Forma de Pagamento",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    referencia = forms.CharField(
        max_length=100,
        required=False,
        label="Referência/Comprovante",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número do comprovante, PIX, etc.'
        })
    )
    
    observacoes = forms.CharField(
        required=False,
        label="Observações",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2
        })
    )
    
    def __init__(self, venda, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.venda = venda
        
        # Definir valor máximo como o valor pendente
        self.fields['valor'].widget.attrs['max'] = str(self.venda.valor_pendente)
        self.fields['valor'].help_text = f"Valor pendente: R$ {self.venda.valor_pendente:,.2f}"
    
    def clean_valor(self):
        valor = self.cleaned_data['valor']
        
        if valor > self.venda.valor_pendente:
            raise ValidationError(
                f"Valor não pode ser maior que o pendente: R$ {self.venda.valor_pendente:,.2f}"
            )
        
        return valor
    
    def to_service_data(self):
        """Converte dados do form para o formato esperado pelo service"""
        return {
            'valor': self.cleaned_data['valor'],
            'forma_pagamento': self.cleaned_data['forma_pagamento'],
            'referencia': self.cleaned_data.get('referencia', ''),
            'observacoes': self.cleaned_data.get('observacoes', ''),
        }


class FiltrarVendasForm(forms.Form):
    """
    Form para filtrar listagem de vendas
    """
    busca = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código, cliente, documento...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + STATUS_VENDA_CHOICES,
        required=False,
        label="Status",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    data_inicio = forms.DateField(
        required=False,
        label="Data Início",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        label="Data Fim",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_inicio > data_fim:
            raise ValidationError("Data início deve ser anterior à data fim.")
        
        return cleaned_data


class CriarClienteRapidoForm(forms.ModelForm):
    """
    Form para criar cliente rapidamente durante uma venda
    """
    class Meta:
        model = Pessoa
        fields = ['nome', 'tipo_doc', 'doc', 'nascimento', 'telefone1', 'email1']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_doc': forms.Select(attrs={'class': 'form-select'}),
            'doc': forms.TextInput(attrs={'class': 'form-control'}),
            'nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefone1': forms.TextInput(attrs={'class': 'form-control'}),
            'email1': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_doc(self):
        documento = self.cleaned_data['doc']
        tipo_documento = self.cleaned_data.get('tipo_doc')
        
        # Verificar se já existe
        if Pessoa.objects.filter(
            doc=documento,
            tipo_doc=tipo_documento
        ).exists():
            raise ValidationError("Já existe uma pessoa com este documento.")
        
        return documento