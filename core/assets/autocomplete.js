/**
 * Componente de Autocomplete reutilizável
 * Usado para campos de busca com HTMX
 */
class AutocompleteField {
    constructor(options) {
        this.searchInput = options.searchInput;
        this.hiddenInput = options.hiddenInput;
        this.resultsContainer = options.resultsContainer;
        this.selectedDisplay = options.selectedDisplay;
        this.selectedText = options.selectedText;
        this.clearButton = options.clearButton;
        this.onSelect = options.onSelect || this.defaultOnSelect.bind(this);
        
        this.isOpen = false;
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        // Mostrar/esconder resultados baseado no foco e conteúdo
        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.length >= 2) {
                this.showResults();
            }
        });

        this.searchInput.addEventListener('input', () => {
            if (this.searchInput.value.length >= 2) {
                this.showResults();
                // Limpa seleção anterior se o usuário digitar novamente
                if (this.hiddenInput.value) {
                    this.clearSelection();
                }
            } else {
                this.hideResults();
            }
        });

        // Fechar autocomplete ao clicar fora
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });

        // Delegação de evento para clique nos itens
        this.resultsContainer.addEventListener('click', (e) => {
            const item = e.target.closest('.autocomplete-item');
            if (item && item.dataset.pessoaId) {
                this.selectItem(item);
            }
        });

        // Hover nos itens
        this.resultsContainer.addEventListener('mouseover', (e) => {
            const item = e.target.closest('.autocomplete-item');
            if (item) {
                this.clearHover();
                item.classList.add('bg-light');
            }
        });

        this.resultsContainer.addEventListener('mouseout', (e) => {
            const item = e.target.closest('.autocomplete-item');
            if (item) {
                item.classList.remove('bg-light');
            }
        });

        // Botão de limpar seleção
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => {
                this.clearSelection();
            });
        }
    }
    
    showResults() {
        this.resultsContainer.style.display = 'block';
        this.isOpen = true;
    }
    
    hideResults() {
        this.resultsContainer.style.display = 'none';
        this.isOpen = false;
    }
    
    clearHover() {
        this.resultsContainer.querySelectorAll('.autocomplete-item').forEach(item => {
            item.classList.remove('bg-light');
        });
    }
    
    selectItem(item) {
        const pessoaId = item.dataset.pessoaId;
        const pessoaNome = item.dataset.pessoaNome;
        const pessoaDoc = item.dataset.pessoaDoc;
        
        this.onSelect(pessoaId, pessoaNome, pessoaDoc);
        this.hideResults();
    }
    
    defaultOnSelect(pessoaId, pessoaNome, pessoaDoc) {
        // Define os valores nos campos
        this.hiddenInput.value = pessoaId;
        this.searchInput.value = `${pessoaNome} - ${pessoaDoc}`;
        
        // Mostra a seleção se os elementos existirem
        if (this.selectedText) {
            this.selectedText.textContent = `${pessoaNome} - ${pessoaDoc}`;
        }
        if (this.selectedDisplay) {
            this.selectedDisplay.style.display = 'block';
        }
    }
    
    clearSelection() {
        this.hiddenInput.value = '';
        this.searchInput.value = '';
        
        if (this.selectedDisplay) {
            this.selectedDisplay.style.display = 'none';
        }
        
        this.hideResults();
    }
}

// Função global para compatibilidade com templates existentes
window.selecionarPessoa = function(pessoaId, pessoaNome, pessoaDoc) {
    // Esta função será sobrescrita pelo autocomplete específico de cada modal
    console.warn('selecionarPessoa não foi inicializada corretamente');
};

window.limparSelecaoPessoa = function() {
    // Esta função será sobrescrita pelo autocomplete específico de cada modal  
    console.warn('limparSelecaoPessoa não foi inicializada corretamente');
};

// Exporta a classe para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutocompleteField;
}

// Disponibiliza globalmente
window.AutocompleteField = AutocompleteField;