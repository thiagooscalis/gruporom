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


class AutocompleteWidget(forms.HiddenInput):
    """
    Widget de autocomplete usando HTMX + Tailwind CSS
    
    HTMX gerencia as requisições e Alpine.js minimal para estado
    """
    
    def __init__(self, search_url=None, search_placeholder="Digite para buscar...", 
                 selected_label="Item selecionado:", min_length=2, attrs=None):
        self.search_url = search_url
        self.search_placeholder = search_placeholder
        self.selected_label = selected_label
        self.min_length = min_length
        
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # Campo hidden para o valor real
        hidden_html = super().render(name, value, attrs, renderer)
        
        # Gerar IDs únicos
        hidden_id = attrs.get('id', f'id_{name}') if attrs else f'id_{name}'
        search_id = f'{hidden_id}_search'
        results_id = f'{hidden_id}_results'
        
        # Buscar valor inicial se existe
        initial_display = ""
        if value:
            try:
                from core.models import Pessoa
                obj = Pessoa.objects.get(pk=value)
                initial_display = f"{obj.nome} ({obj.doc})"
            except:
                initial_display = ""
        
        # HTML do componente com Alpine.js mínimo usando data attributes
        widget_html = f'''
        <div class="relative" 
             x-data="autocompleteWidget()"
             data-initial-display="{initial_display}"
             data-initial-value="{value or ''}"
             data-widget-id="{hidden_id}">
            
            <!-- Campo de busca visível -->
            <div class="mb-4">
                <input type="text" 
                       id="{search_id}"
                       @input="if($event.target.value.length >= {self.min_length}) showResults = true; else {{ showResults = false; document.getElementById('{results_id}').innerHTML = ''; }}"
                       @focus="if($event.target.value.length >= {self.min_length}) showResults = true"
                       hx-get="{self.search_url}"
                       hx-trigger="keyup[target.value.length >= {self.min_length}] changed delay:300ms"
                       hx-target="#{results_id}"
                       hx-swap="innerHTML"
                       hx-vals="js:{{q: document.getElementById('{search_id}').value}}"
                       class="mt-1 block w-full px-3 py-2 border border-gray-200 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 placeholder-slate-400"
                       placeholder="{self.search_placeholder}"
                       autocomplete="off">
            </div>
            
            <!-- Container para resultados do autocomplete -->
            <div x-show="showResults" 
                 @click.outside="showResults = false"
                 x-transition
                 class="absolute z-20 mt-1 w-full bg-white border border-gray-200 shadow-lg max-h-60 rounded-md py-1 text-base overflow-auto focus:outline-none sm:text-sm">
                
                <!-- Resultados carregados via HTMX -->
                <div id="{results_id}">
                    <!-- Resultados aparecerão aqui via HTMX -->
                </div>
            </div>
            
            <!-- Item selecionado -->
            <div x-show="selectedItem" x-transition class="mt-3">
                <div class="bg-success-50 border border-success-200 rounded-md p-3 flex items-center justify-between">
                    <div class="flex items-center">
                        <svg class="w-5 h-5 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                        <div>
                            <span class="font-medium text-success-800">{self.selected_label}</span>
                            <span class="text-success-700" x-text="selectedItem"></span>
                        </div>
                    </div>
                    <button type="button" 
                            @click="clearSelection()"
                            class="text-success-500 hover:text-success-700 focus:outline-none focus:ring-2 focus:ring-success-500 focus:ring-offset-2 rounded-md p-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        // Função Alpine.js para autocomplete
        window.autocompleteWidget = function() {{
            return {{
                selectedItem: null,
                selectedId: null,
                showResults: false,
                
                init() {{
                    // Ler valores iniciais dos data attributes
                    const container = this.$el;
                    const initialDisplay = container.dataset.initialDisplay;
                    const initialValue = container.dataset.initialValue;
                    
                    if (initialDisplay && initialValue) {{
                        this.selectedItem = initialDisplay;
                        this.selectedId = initialValue;
                    }}
                    
                    // Bind eventos HTMX
                    const resultsDiv = container.querySelector('#{results_id}');
                    resultsDiv.addEventListener('htmx:afterSwap', () => {{
                        this.bindResultsClick();
                    }});
                }},
                
                bindResultsClick() {{
                    const container = this.$el;
                    container.querySelectorAll('#{results_id} [data-pessoa-id]').forEach(item => {{
                        item.onclick = () => {{
                            const id = item.dataset.pessoaId;
                            const nome = item.dataset.pessoaNome;
                            const doc = item.dataset.pessoaDoc;
                            
                            this.selectedId = id;
                            this.selectedItem = nome + ' (' + doc + ')';
                            this.showResults = false;
                            
                            document.getElementById('{hidden_id}').value = id;
                            document.getElementById('{hidden_id}').dispatchEvent(new Event('change', {{ bubbles: true }}));
                            document.getElementById('{search_id}').value = '';
                            document.getElementById('{results_id}').innerHTML = '';
                        }};
                    }});
                }},
                
                clearSelection() {{
                    this.selectedItem = null;
                    this.selectedId = null;
                    this.showResults = false;
                    document.getElementById('{hidden_id}').value = '';
                    document.getElementById('{hidden_id}').dispatchEvent(new Event('change'));
                    document.getElementById('{search_id}').value = '';
                    document.getElementById('{results_id}').innerHTML = '';
                }}
            }}
        }};
        </script>
        '''
        
        return mark_safe(hidden_html + widget_html)


class TagsWidget(MultiSelectWidget):
    """
    Widget especializado para tags (permite criação de novas opções)
    """
    
    def __init__(self, attrs=None, **kwargs):
        kwargs.setdefault('create', True)
        kwargs.setdefault('placeholder', 'Digite para adicionar tags...')
        kwargs.setdefault('create_text', 'Criar tag: ')
        super().__init__(attrs=attrs, **kwargs)