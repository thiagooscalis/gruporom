# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import SelectMultiple
from django.utils.safestring import mark_safe
import json


class MultiSelectWidget(SelectMultiple):
    """
    Widget customizado para campos ManyToMany com Tom-Select
    Fornece interface moderna com busca, tags e multiselect
    """
    
    def __init__(self, attrs=None, choices=(), 
                 placeholder="Selecione...", 
                 search_placeholder="Digite para buscar...",
                 no_results_text="Nenhum resultado encontrado",
                 max_options=None,
                 create=False,
                 create_text="Adicionar: ",
                 remove_button=True,
                 clear_button=True,
                 allow_empty_option=False):
        
        default_attrs = {
            'class': 'form-select tom-select-field',
            'data-placeholder': placeholder,
            'data-search-placeholder': search_placeholder,
            'data-no-results-text': no_results_text,
            'data-remove-button': str(remove_button).lower(),
            'data-clear-button': str(clear_button).lower(),
            'data-allow-empty': str(allow_empty_option).lower(),
        }
        
        if max_options:
            default_attrs['data-max-options'] = str(max_options)
        
        if create:
            default_attrs['data-create'] = 'true'
            default_attrs['data-create-text'] = create_text
        
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(attrs=default_attrs, choices=choices)
    
    def render(self, name, value, attrs=None, renderer=None):
        # Renderizar o select normal
        html = super().render(name, value, attrs, renderer)
        
        # Adicionar script de inicialização Tom-Select
        widget_id = attrs.get('id', f'id_{name}') if attrs else f'id_{name}'
        
        script = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                if (typeof TomSelect !== 'undefined') {{
                    const element = document.getElementById('{widget_id}');
                    if (element && !element.tomselect) {{
                        const config = {{
                            plugins: ['remove_button', 'clear_button'],
                            persist: false,
                            createOnBlur: false,
                            create: element.dataset.create === 'true',
                            maxOptions: element.dataset.maxOptions ? parseInt(element.dataset.maxOptions) : null,
                            placeholder: element.dataset.placeholder || 'Selecione...',
                            searchField: ['text', 'value'],
                            sortField: [
                                {{field: 'text', direction: 'asc'}}
                            ],
                            dropdownParent: 'body',
                            render: {{
                                no_results: function(data, escape) {{
                                    return '<div class="no-results">' + escape(element.dataset.noResultsText || 'Nenhum resultado encontrado') + '</div>';
                                }},
                                option_create: function(data, escape) {{
                                    return '<div class="create">' + escape(element.dataset.createText || 'Adicionar: ') + '<strong>' + escape(data.input) + '</strong></div>';
                                }}
                            }}
                        }};
                        
                        // Remover plugins se desabilitados
                        if (element.dataset.removeButton === 'false') {{
                            config.plugins = config.plugins.filter(p => p !== 'remove_button');
                        }}
                        if (element.dataset.clearButton === 'false') {{
                            config.plugins = config.plugins.filter(p => p !== 'clear_button');
                        }}
                        
                        // Inicializar Tom-Select
                        const tomSelect = new TomSelect(element, config);
                        
                        // Aplicar estilos Bootstrap
                        const wrapper = tomSelect.wrapper;
                        wrapper.classList.add('tom-select-bootstrap');
                    }}
                }} else {{
                    console.warn('Tom-Select não está carregado. Certifique-se de incluir a biblioteca.');
                }}
            }});
        </script>
        """
        
        return mark_safe(html + script)
    
    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/css/tom-select.bootstrap5.css',
                'css/tom-select-custom.css',  # CSS customizado para tema
            )
        }
        js = (
            'https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/js/tom-select.complete.min.js',
            'js/tom-select-init.js',  # Script de inicialização customizado
        )


class AutocompleteWidget(forms.TextInput):
    """
    Widget de autocomplete para campos ForeignKey
    Usa HTMX para busca dinâmica
    """
    
    def __init__(self, model=None, search_url=None, attrs=None, 
                 min_length=2, placeholder="Digite para buscar..."):
        self.model = model
        self.search_url = search_url
        self.min_length = min_length
        
        default_attrs = {
            'class': 'form-control autocomplete-field',
            'placeholder': placeholder,
            'autocomplete': 'off',
            'data-min-length': str(min_length),
        }
        
        if search_url:
            default_attrs.update({
                'hx-get': search_url,
                'hx-trigger': f'keyup changed delay:300ms[target.value.length>={min_length}]',
                'hx-target': '#autocomplete-results',
                'hx-swap': 'innerHTML',
            })
        
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(attrs=default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        # Container para resultados
        results_html = '''
        <div class="position-relative">
            <div id="autocomplete-results" class="autocomplete-results"></div>
        </div>
        '''
        
        return mark_safe(html + results_html)


class TagsWidget(MultiSelectWidget):
    """
    Widget especializado para tags (permite criação de novas opções)
    """
    
    def __init__(self, attrs=None, **kwargs):
        kwargs.setdefault('create', True)
        kwargs.setdefault('placeholder', 'Digite para adicionar tags...')
        kwargs.setdefault('create_text', 'Criar tag: ')
        super().__init__(attrs=attrs, **kwargs)