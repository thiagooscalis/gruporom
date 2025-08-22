# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import SelectMultiple
from django.utils.safestring import mark_safe


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


class MultipleAutocompleteWidget(forms.MultipleHiddenInput):
    """
    Widget de autocomplete múltiplo usando HTMX + Tailwind CSS
    
    Similar ao AutocompleteWidget mas permite seleção múltipla
    """
    
    def __init__(self, search_url=None, search_placeholder="Digite para buscar...", 
                 selected_label="Itens selecionados:", min_length=2, attrs=None):
        self.search_url = search_url
        self.search_placeholder = search_placeholder
        self.selected_label = selected_label
        self.min_length = min_length
        
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # Campos hidden para os valores múltiplos
        hidden_html = super().render(name, value, attrs, renderer)
        
        # Gerar IDs únicos
        hidden_id = attrs.get('id', f'id_{name}') if attrs else f'id_{name}'
        search_id = f'{hidden_id}_search'
        results_id = f'{hidden_id}_results'
        container_id = f'{hidden_id}_container'
        
        # Buscar valores iniciais se existem
        initial_items = []
        if value:
            try:
                from core.models import Pessoa
                if isinstance(value, (list, tuple)):
                    for val in value:
                        try:
                            obj = Pessoa.objects.get(pk=val)
                            initial_items.append({
                                'id': str(obj.pk),
                                'nome': obj.nome,
                                'doc': obj.doc
                            })
                        except:
                            pass
                else:
                    obj = Pessoa.objects.get(pk=value)
                    initial_items.append({
                        'id': str(obj.pk),
                        'nome': obj.nome,
                        'doc': obj.doc
                    })
            except:
                pass
        
        initial_items_json = str(initial_items).replace("'", '"')
        
        # HTML do componente com Alpine.js
        widget_html = f'''
        <div class="relative" 
             x-data="multipleAutocompleteWidget()"
             data-initial-items='{initial_items_json}'
             data-widget-id="{hidden_id}"
             data-field-name="{name}">
            
            <!-- Campo de busca visível -->
            <div class="mb-4">
                <input type="text" 
                       id="{search_id}"
                       x-model="searchQuery"
                       @input="onSearchInput()"
                       @focus="onFocus()"
                       class="mt-1 block w-full px-3 py-2 border border-gray-200 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 placeholder-slate-400"
                       placeholder="{self.search_placeholder}"
                       autocomplete="off">
            </div>
            
            <!-- Container para resultados do autocomplete -->
            <div x-show="showResults" 
                 @click.outside="showResults = false"
                 x-transition
                 class="absolute z-20 mt-1 w-full bg-white border border-gray-200 shadow-lg max-h-60 rounded-md py-1 text-base overflow-auto focus:outline-none sm:text-sm">
                
                <!-- Loading state -->
                <div x-show="loading" class="px-3 py-2 text-gray-500">
                    <div class="flex items-center">
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Buscando...
                    </div>
                </div>
                
                <!-- Resultados carregados via HTMX -->
                <div id="{results_id}">
                    <!-- Resultados aparecerão aqui via HTMX -->
                </div>
            </div>
            
            <!-- Container para itens selecionados -->
            <div class="mt-3" x-show="selectedItems.length > 0">
                <div class="bg-success-50 border border-success-200 rounded-md p-3">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-success-800">{self.selected_label}</span>
                        <button type="button" 
                                @click="clearAll()"
                                class="text-success-500 hover:text-success-700 text-sm">
                            Limpar todos
                        </button>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        <template x-for="item in selectedItems" :key="item.id">
                            <div class="inline-flex items-center bg-white border border-success-300 text-success-800 text-sm font-medium px-2.5 py-1 rounded-full">
                                <span x-text="item.nome" class="mr-1"></span>
                                <button type="button" 
                                        @click="removeItem(item.id)"
                                        class="ml-1 text-success-600 hover:text-success-800 focus:outline-none rounded-full p-0.5">
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
            
            <!-- Mensagem quando vazio -->
            <div class="mt-3" x-show="selectedItems.length === 0">
                <div class="bg-gray-50 border border-gray-200 rounded-md p-3 text-center text-gray-500">
                    <svg class="w-5 h-5 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                    </svg>
                    <div class="text-sm">Nenhum item selecionado</div>
                </div>
            </div>
            
            <!-- Container para campos hidden dinâmicos -->
            <div id="{container_id}">
                <!-- Campos hidden serão inseridos aqui via JavaScript -->
            </div>
        </div>
        
        <script>
        // Função Alpine.js para autocomplete múltiplo
        window.multipleAutocompleteWidget = function() {{
            return {{
                selectedItems: [],
                searchQuery: '',
                results: [],
                showResults: false,
                loading: false,
                debounceTimer: null,
                
                init() {{
                    // Ler valores iniciais dos data attributes
                    const container = this.$el;
                    const initialItems = JSON.parse(container.dataset.initialItems || '[]');
                    const fieldName = container.dataset.fieldName;
                    
                    if (initialItems.length > 0) {{
                        this.selectedItems = initialItems;
                        this.updateHiddenFields();
                    }}
                    
                    // Bind eventos HTMX
                    const resultsDiv = container.querySelector('#{results_id}');
                    resultsDiv.addEventListener('htmx:afterSwap', () => {{
                        this.bindResultsClick();
                    }});
                }},
                
                onSearchInput() {{
                    clearTimeout(this.debounceTimer);
                    
                    if (this.searchQuery.length < {self.min_length}) {{
                        this.showResults = false;
                        this.results = [];
                        return;
                    }}
                    
                    this.debounceTimer = setTimeout(() => {{
                        this.fetchResults();
                    }}, 300);
                }},
                
                onFocus() {{
                    if (this.searchQuery.length >= {self.min_length} && this.results.length > 0) {{
                        this.showResults = true;
                    }}
                }},
                
                fetchResults() {{
                    this.loading = true;
                    this.showResults = true;
                    
                    // Usar HTMX para buscar resultados
                    const url = new URL('{self.search_url}', window.location.origin);
                    url.searchParams.set('q', this.searchQuery);
                    
                    htmx.ajax('GET', url.toString(), {{
                        target: '#{results_id}',
                        swap: 'innerHTML'
                    }}).then(() => {{
                        this.loading = false;
                        this.bindResultsClick();
                    }}).catch(() => {{
                        this.loading = false;
                        this.showResults = false;
                    }});
                }},
                
                bindResultsClick() {{
                    const container = this.$el;
                    container.querySelectorAll('#{results_id} [data-pessoa-id]').forEach(item => {{
                        // Verificar se já está selecionado
                        const id = item.dataset.pessoaId;
                        const isSelected = this.selectedItems.some(selected => selected.id === id);
                        
                        if (isSelected) {{
                            item.classList.add('bg-primary-50', 'text-primary-900');
                            item.innerHTML += ' <span class="text-primary-600 font-medium">(Selecionado)</span>';
                        }}
                        
                        item.onclick = () => {{
                            if (!isSelected) {{
                                const nome = item.dataset.pessoaNome;
                                const doc = item.dataset.pessoaDoc;
                                
                                this.selectedItems.push({{
                                    id: id,
                                    nome: nome,
                                    doc: doc
                                }});
                                
                                this.updateHiddenFields();
                                this.searchQuery = '';
                                this.showResults = false;
                                document.getElementById('{results_id}').innerHTML = '';
                            }}
                        }};
                    }});
                }},
                
                removeItem(itemId) {{
                    this.selectedItems = this.selectedItems.filter(item => item.id !== itemId);
                    this.updateHiddenFields();
                }},
                
                clearAll() {{
                    this.selectedItems = [];
                    this.updateHiddenFields();
                }},
                
                updateHiddenFields() {{
                    const container = document.getElementById('{container_id}');
                    const fieldName = this.$el.dataset.fieldName;
                    
                    // Remover campos hidden existentes
                    container.innerHTML = '';
                    
                    // Criar novos campos hidden para cada item selecionado
                    this.selectedItems.forEach(item => {{
                        const hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = fieldName;
                        hiddenInput.value = item.id;
                        container.appendChild(hiddenInput);
                    }});
                    
                    // Disparar evento change para formulários que dependem disso
                    const changeEvent = new Event('change', {{ bubbles: true }});
                    container.dispatchEvent(changeEvent);
                }}
            }}
        }}
        </script>
        '''
        
        return mark_safe(hidden_html + widget_html)


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