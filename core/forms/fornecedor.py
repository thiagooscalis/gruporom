from django import forms
from django.urls import reverse
from core.models import Fornecedor, Pessoa
from core.choices import TIPO_EMPRESA_CHOICES
from core.fields import AutocompleteField


class FornecedorForm(forms.ModelForm):
    # Campo de autocomplete customizado
    pessoa = AutocompleteField(
        queryset=Pessoa.objects.all(),
        search_url=None,  # Será definido no __init__
        search_placeholder="Digite o nome, documento ou email da pessoa...",
        selected_label="Pessoa selecionada:",
        label="Pessoa"
    )

    class Meta:
        model = Fornecedor
        fields = ['pessoa', 'tipo_empresa', 'empresas']
        widgets = {
            'tipo_empresa': forms.Select(attrs={'class': 'form-select'}),
            'empresas': forms.CheckboxSelectMultiple()
        }
        labels = {
            'tipo_empresa': 'Tipo de Empresa',
            'empresas': 'Empresas do Grupo ROM'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar URL de busca para o autocomplete
        search_url = reverse('buscar_pessoas', kwargs={'area': 'administracao'}) + '?all=true'
        self.fields['pessoa'].widget.search_url = search_url
        
        # Filtrar apenas empresas do Grupo ROM
        self.fields['empresas'].queryset = Pessoa.objects.filter(
            empresa_gruporom=True
        ).order_by('nome')

    def clean_pessoa(self):
        """Valida o campo pessoa"""
        pessoa = self.cleaned_data.get('pessoa')
        if pessoa:
            # Verifica se a pessoa já é fornecedor (exceto no caso de edição)
            if hasattr(pessoa, 'fornecedor') and (not self.instance.pk or pessoa.fornecedor.pk != self.instance.pk):
                raise forms.ValidationError("Esta pessoa já é um fornecedor.")
            return pessoa
        else:
            raise forms.ValidationError("Selecione uma pessoa.")

    def save(self, commit=True):
        """Override save to handle M2M field properly"""
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            # Save M2M field after the instance is saved
            self.save_m2m()
        
        return instance