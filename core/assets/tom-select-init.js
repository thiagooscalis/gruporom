/**
 * Inicializador global para Tom-Select
 * Configura automaticamente todos os campos .tom-select-field
 */

// Configuração padrão para todos os Tom-Select
const TOM_SELECT_DEFAULTS = {
    plugins: ['remove_button', 'clear_button'],
    persist: false,
    createOnBlur: false,
    searchField: ['text', 'value'],
    sortField: [
        {field: 'text', direction: 'asc'}
    ],
    dropdownParent: 'body',
    placeholder: 'Selecione...',
    render: {
        no_results: function(data, escape) {
            const element = this.input;
            const text = element.dataset.noResultsText || 'Nenhum resultado encontrado';
            return '<div class="no-results">' + escape(text) + '</div>';
        },
        option_create: function(data, escape) {
            const element = this.input;
            const text = element.dataset.createText || 'Adicionar: ';
            return '<div class="create">' + text + '<strong>' + escape(data.input) + '</strong></div>';
        }
    },
    onItemAdd: function(value, item) {
        // Limpar o campo de busca após adicionar item
        this.setTextboxValue('');
        this.refreshState();
    }
};

/**
 * Inicializa Tom-Select em um elemento específico
 */
function initTomSelect(element) {
    if (element.tomselect) {
        return element.tomselect; // Já inicializado
    }
    
    const config = {...TOM_SELECT_DEFAULTS};
    
    // Configurações baseadas em data attributes
    if (element.dataset.placeholder) {
        config.placeholder = element.dataset.placeholder;
    }
    
    if (element.dataset.maxOptions) {
        config.maxOptions = parseInt(element.dataset.maxOptions);
    }
    
    if (element.dataset.create === 'true') {
        config.create = true;
    }
    
    // Remover plugins se desabilitados
    if (element.dataset.removeButton === 'false') {
        config.plugins = config.plugins.filter(p => p !== 'remove_button');
    }
    
    if (element.dataset.clearButton === 'false') {
        config.plugins = config.plugins.filter(p => p !== 'clear_button');
    }
    
    // Para campos HTMX, adicionar suporte a recarregamento
    if (element.hasAttribute('hx-get') || element.closest('[hx-target]')) {
        config.onInitialize = function() {
            const tomSelect = this;
            
            // Escutar eventos HTMX para reinicializar se necessário
            document.addEventListener('htmx:afterSwap', function(e) {
                if (e.target.contains && e.target.contains(element)) {
                    // Elemento foi alterado via HTMX, pode precisar reinicializar
                    setTimeout(() => {
                        if (!element.tomselect) {
                            initTomSelect(element);
                        }
                    }, 100);
                }
            });
        };
    }
    
    try {
        const tomSelect = new TomSelect(element, config);
        
        // Adicionar classe Bootstrap ao wrapper
        const wrapper = tomSelect.wrapper;
        wrapper.classList.add('tom-select-bootstrap');
        
        // Eventos personalizados
        tomSelect.on('item_add', function(value, item) {
            // Disparar evento customizado
            element.dispatchEvent(new CustomEvent('tomselect:add', {
                detail: {value, item}
            }));
        });
        
        tomSelect.on('item_remove', function(value) {
            element.dispatchEvent(new CustomEvent('tomselect:remove', {
                detail: {value}
            }));
        });
        
        return tomSelect;
        
    } catch (error) {
        console.error('Erro ao inicializar Tom-Select:', error);
        return null;
    }
}

/**
 * Inicializa todos os Tom-Select na página
 */
function initAllTomSelect() {
    if (typeof TomSelect === 'undefined') {
        console.warn('Tom-Select não está disponível. Certifique-se de incluir a biblioteca.');
        return;
    }
    
    document.querySelectorAll('.tom-select-field:not([data-tom-select-initialized])').forEach(element => {
        initTomSelect(element);
        element.setAttribute('data-tom-select-initialized', 'true');
    });
}

/**
 * Reinicializar Tom-Select após mudanças no DOM (HTMX, modais, etc.)
 */
function reinitTomSelect(container = document) {
    container.querySelectorAll('.tom-select-field').forEach(element => {
        if (!element.tomselect) {
            initTomSelect(element);
            element.setAttribute('data-tom-select-initialized', 'true');
        }
    });
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initAllTomSelect);

// Reinicializar após eventos HTMX
document.addEventListener('htmx:afterSwap', function(e) {
    reinitTomSelect(e.detail.target);
});

// Reinicializar quando modais são mostrados
document.addEventListener('shown.bs.modal', function(e) {
    reinitTomSelect(e.target);
});

// Limpar Tom-Select quando modal é escondido (evitar vazamentos de memória)
document.addEventListener('hidden.bs.modal', function(e) {
    e.target.querySelectorAll('.tom-select-field').forEach(element => {
        if (element.tomselect) {
            element.tomselect.destroy();
            element.removeAttribute('data-tom-select-initialized');
        }
    });
});

// Exportar funções globalmente
window.initTomSelect = initTomSelect;
window.initAllTomSelect = initAllTomSelect;
window.reinitTomSelect = reinitTomSelect;

// Adicionar suporte a máscaras se disponível
if (typeof initMasks === 'function') {
    document.addEventListener('tomselect:add', function(e) {
        // Reinicializar máscaras após adicionar item
        setTimeout(() => initMasks(), 100);
    });
}