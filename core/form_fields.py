# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from .widgets import MultiSelectWidget, AutocompleteWidget, TagsWidget


class ModelMultiSelectField(forms.ModelMultipleChoiceField):
    """
    Campo global para seleção múltipla de modelos com interface moderna
    Usa Tom-Select para melhor UX
    """
    
    def __init__(self, queryset, widget=None, **kwargs):
        # Extrair parâmetros específicos do Tom-Select
        tom_select_options = {}
        for key in ['placeholder', 'search_placeholder', 'no_results_text', 
                   'max_options', 'create', 'create_text', 'remove_button', 
                   'clear_button', 'allow_empty_option']:
            if key in kwargs:
                tom_select_options[key] = kwargs.pop(key)
        
        # Se não foi fornecido widget customizado, usar MultiSelectWidget
        if widget is None:
            widget = MultiSelectWidget(**tom_select_options)
        
        super().__init__(queryset=queryset, widget=widget, **kwargs)
    
    def label_from_instance(self, obj):
        """
        Personaliza como o label é gerado para cada opção
        Pode ser sobrescrito em subclasses para customização específica
        """
        return str(obj)


class PessoasMultiSelectField(ModelMultiSelectField):
    """
    Campo especializado para seleção múltipla de pessoas
    """
    
    def __init__(self, queryset, **kwargs):
        kwargs.setdefault('placeholder', 'Selecione pessoas...')
        kwargs.setdefault('search_placeholder', 'Digite nome ou documento...')
        kwargs.setdefault('no_results_text', 'Nenhuma pessoa encontrada')
        super().__init__(queryset=queryset, **kwargs)
    
    def label_from_instance(self, obj):
        """Formato: Nome - Documento"""
        if hasattr(obj, 'doc') and obj.doc:
            return f"{obj.nome} - {obj.doc}"
        return obj.nome


class PaisesMultiSelectField(ModelMultiSelectField):
    """
    Campo especializado para seleção múltipla de países
    """
    
    def __init__(self, queryset, **kwargs):
        kwargs.setdefault('placeholder', 'Selecione países...')
        kwargs.setdefault('search_placeholder', 'Digite o nome do país...')
        kwargs.setdefault('no_results_text', 'Nenhum país encontrado')
        super().__init__(queryset=queryset, **kwargs)
    
    def label_from_instance(self, obj):
        """Formato: Nome (Código ISO)"""
        if hasattr(obj, 'iso') and obj.iso:
            return f"{obj.nome} ({obj.iso})"
        return obj.nome


class EmpresasMultiSelectField(ModelMultiSelectField):
    """
    Campo especializado para seleção múltipla de empresas
    """
    
    def __init__(self, queryset, **kwargs):
        kwargs.setdefault('placeholder', 'Selecione empresas...')
        kwargs.setdefault('search_placeholder', 'Digite o nome da empresa...')
        kwargs.setdefault('no_results_text', 'Nenhuma empresa encontrada')
        super().__init__(queryset=queryset, **kwargs)
    
    def label_from_instance(self, obj):
        """Formato: Nome - CNPJ (se disponível)"""
        if hasattr(obj, 'doc') and obj.doc and obj.tipo_doc == 'CNPJ':
            return f"{obj.nome} - {obj.doc}"
        return obj.nome


class GruposMultiSelectField(ModelMultiSelectField):
    """
    Campo especializado para seleção múltipla de grupos de usuário
    """
    
    def __init__(self, queryset, **kwargs):
        kwargs.setdefault('placeholder', 'Selecione grupos...')
        kwargs.setdefault('search_placeholder', 'Digite o nome do grupo...')
        kwargs.setdefault('no_results_text', 'Nenhum grupo encontrado')
        kwargs.setdefault('max_options', 10)  # Limitar grupos por usuário
        super().__init__(queryset=queryset, **kwargs)


class TurnosMultiSelectField(ModelMultiSelectField):
    """
    Campo especializado para seleção múltipla de turnos
    """
    
    def __init__(self, queryset, **kwargs):
        kwargs.setdefault('placeholder', 'Selecione turnos...')
        kwargs.setdefault('search_placeholder', 'Digite o nome do turno...')
        kwargs.setdefault('no_results_text', 'Nenhum turno encontrado')
        super().__init__(queryset=queryset, **kwargs)
    
    def label_from_instance(self, obj):
        """Formato: Nome - Horário"""
        if hasattr(obj, 'hora_inicio') and hasattr(obj, 'hora_fim'):
            return f"{obj.nome} - {obj.hora_inicio} às {obj.hora_fim}"
        return obj.nome


class AeroportosMultiSelectField(ModelMultiSelectField):
    """
    Campo especializado para seleção múltipla de aeroportos
    """
    
    def __init__(self, queryset, **kwargs):
        kwargs.setdefault('placeholder', 'Selecione aeroportos...')
        kwargs.setdefault('search_placeholder', 'Digite o nome do aeroporto ou código IATA...')
        kwargs.setdefault('no_results_text', 'Nenhum aeroporto encontrado')
        super().__init__(queryset=queryset, **kwargs)
    
    def label_from_instance(self, obj):
        """Formato: Nome (IATA) - Cidade/País"""
        if hasattr(obj, 'iata') and hasattr(obj, 'cidade'):
            cidade_pais = f"{obj.cidade.nome}"
            if hasattr(obj.cidade, 'pais'):
                cidade_pais += f"/{obj.cidade.pais.nome}"
            return f"{obj.nome} ({obj.iata}) - {cidade_pais}"
        return obj.nome


class AeroportoField(forms.ModelChoiceField):
    """
    Campo singular de aeroporto com busca Tom-Select
    """
    
    def __init__(self, queryset, **kwargs):
        # Parâmetros específicos do Tom-Select
        tom_select_options = {}
        for key in ['placeholder', 'search_placeholder', 'no_results_text']:
            if key in kwargs:
                tom_select_options[key] = kwargs.pop(key)
        
        # Configurações padrão
        tom_select_options.setdefault('placeholder', 'Selecione um aeroporto...')
        tom_select_options.setdefault('search_placeholder', 'Digite o nome ou código IATA...')
        tom_select_options.setdefault('no_results_text', 'Nenhum aeroporto encontrado')
        
        # Widget Tom-Select para campo singular
        from .widgets import MultiSelectWidget
        widget = MultiSelectWidget(
            **tom_select_options,
            max_options=1,  # Apenas um aeroporto
            remove_button=False,  # Não precisa de botão remover em campo singular
        )
        # Converter para select simples
        widget.allow_multiple_selected = False
        
        kwargs['widget'] = forms.Select(attrs={
            'class': 'form-select tom-select-field',
            'data-placeholder': tom_select_options['placeholder'],
            'data-search-placeholder': tom_select_options['search_placeholder'],
            'data-no-results-text': tom_select_options['no_results_text'],
        })
        
        super().__init__(queryset=queryset, **kwargs)
    
    def label_from_instance(self, obj):
        """Formato: Nome (IATA) - Cidade/País"""
        if hasattr(obj, 'iata') and hasattr(obj, 'cidade'):
            cidade_pais = f"{obj.cidade.nome}"
            if hasattr(obj.cidade, 'pais'):
                cidade_pais += f"/{obj.cidade.pais.nome}"
            return f"{obj.nome} ({obj.iata}) - {cidade_pais}"
        return obj.nome


# Funções de conveniência para uso rápido
def create_multiselect_field(model, queryset=None, **kwargs):
    """
    Função de conveniência para criar campo multiselect rapidamente
    
    Exemplo:
    lideres = create_multiselect_field(Pessoa, placeholder="Selecione líderes...")
    """
    if queryset is None:
        queryset = model.objects.all()
    
    return ModelMultiSelectField(queryset=queryset, **kwargs)


def create_pessoas_field(queryset=None, **kwargs):
    """
    Função de conveniência para campo de pessoas
    
    Exemplo:
    colaboradores = create_pessoas_field(Pessoa.objects.filter(tipo_doc='CPF'))
    """
    from .models import Pessoa
    if queryset is None:
        queryset = Pessoa.objects.filter(tipo_doc='CPF')
    
    return PessoasMultiSelectField(queryset=queryset, **kwargs)


def create_paises_field(queryset=None, **kwargs):
    """
    Função de conveniência para campo de países
    
    Exemplo:
    destinos = create_paises_field()
    """
    from .models import Pais
    if queryset is None:
        queryset = Pais.objects.all()
    
    return PaisesMultiSelectField(queryset=queryset, **kwargs)


def create_empresas_field(tipo_empresa=None, **kwargs):
    """
    Função de conveniência para campo de empresas
    
    Exemplo:
    empresas_turismo = create_empresas_field(tipo_empresa='Turismo')
    """
    from .models import Pessoa
    queryset = Pessoa.objects.filter(empresa_gruporom=True)
    
    if tipo_empresa:
        queryset = queryset.filter(tipo_empresa=tipo_empresa)
    
    return EmpresasMultiSelectField(queryset=queryset, **kwargs)


def create_aeroportos_field(queryset=None, multiple=True, **kwargs):
    """
    Função de conveniência para campo de aeroportos
    
    Exemplo:
    aeroporto_embarque = create_aeroportos_field(multiple=False)  # Campo singular
    aeroportos_escala = create_aeroportos_field()  # Campo múltiplo
    """
    from .models import Aeroporto
    if queryset is None:
        queryset = Aeroporto.objects.select_related('cidade__pais').order_by('nome')
    
    if multiple:
        return AeroportosMultiSelectField(queryset=queryset, **kwargs)
    else:
        return AeroportoField(queryset=queryset, **kwargs)


class HTTPSURLField(forms.URLField):
    """
    Campo URLField que assume HTTPS como esquema padrão para resolver warnings do Django 5.2/6.0
    """
    
    def __init__(self, **kwargs):
        kwargs['assume_scheme'] = 'https'
        super().__init__(**kwargs)