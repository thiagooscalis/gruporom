from django import forms
from core.models import Fornecedor, Pessoa
from core.choices import TIPO_EMPRESA_CHOICES


class FornecedorForm(forms.ModelForm):
    # Campo para seleção de pessoa com autocomplete
    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.none(),  # Vazio por padrão
        required=True,
        widget=forms.HiddenInput(),
        label="Pessoa"
    )
    
    # Campo de busca para autocomplete
    pessoa_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome, documento ou email da pessoa...',
            'autocomplete': 'off'
        }),
        label="Buscar Pessoa"
    )

    class Meta:
        model = Fornecedor
        fields = ['pessoa', 'pessoa_search', 'tipo_empresa', 'empresas']
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
        
        # Se for edição, pré-preenche o campo de busca e pessoa selecionada
        if self.instance.pk:
            self.fields['pessoa'].queryset = Pessoa.objects.filter(pk=self.instance.pessoa.pk)
            self.fields['pessoa_search'].initial = f"{self.instance.pessoa.nome} - {self.instance.pessoa.doc}"
        
        # Filtrar apenas empresas do Grupo ROM
        self.fields['empresas'].queryset = Pessoa.objects.filter(
            empresa_gruporom=True
        ).order_by('nome')

    def clean_pessoa(self):
        """Valida o campo pessoa"""
        pessoa_id = self.data.get('pessoa')
        if pessoa_id:
            try:
                pessoa = Pessoa.objects.get(pk=pessoa_id)
                # Verifica se a pessoa já é fornecedor (exceto no caso de edição)
                if hasattr(pessoa, 'fornecedor') and (not self.instance.pk or pessoa.fornecedor.pk != self.instance.pk):
                    raise forms.ValidationError("Esta pessoa já é um fornecedor.")
                return pessoa
            except Pessoa.DoesNotExist:
                raise forms.ValidationError("Pessoa inválida.")
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