/**
 * Componente de Autocomplete Múltiplo para campos ManyToMany
 * Permite seleção de múltiplos itens com busca AJAX
 */
class MultipleAutocompleteField {
    constructor(options) {
        this.searchInput = options.searchInput;
        this.hiddenContainer = options.hiddenContainer;
        this.resultsContainer = options.resultsContainer;
        this.selectedContainer = options.selectedContainer;
        this.searchUrl = options.searchUrl || '';
        this.fieldName = options.fieldName || 'items';
        
        this.selectedItems = new Map(); // ID -> {id, nome, doc}
        this.isOpen = false;
        this.init();
    }
    
    init() {
        this.loadInitialValues();
        this.bindEvents();
    }
    
    loadInitialValues() {
        // Carrega valores já selecionados se existirem inputs hidden
        const hiddenInputs = this.hiddenContainer.querySelectorAll('input[type="hidden"]');
        hiddenInputs.forEach(input => {
            const id = input.value;
            const nome = input.dataset.nome || 'Item selecionado';
            const doc = input.dataset.doc || '';
            if (id) {
                this.selectedItems.set(id, { id, nome, doc });
            }
        });
        this.renderSelectedItems();
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
            } else {
                this.hideResults();
            }
        });

        // Fechar autocomplete ao clicar fora
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && 
                !this.resultsContainer.contains(e.target)) {
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

        // Eventos para remoção de itens selecionados
        this.selectedContainer.addEventListener('click', (e) => {
            if (e.target.closest('.remove-selected-item')) {
                const itemId = e.target.closest('.remove-selected-item').dataset.itemId;
                this.removeItem(itemId);
            }
        });
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
        
        // Não adiciona se já estiver selecionado
        if (!this.selectedItems.has(pessoaId)) {
            this.selectedItems.set(pessoaId, {
                id: pessoaId,
                nome: pessoaNome,
                doc: pessoaDoc
            });
            this.renderSelectedItems();
            this.updateHiddenInputs();
        }
        
        // Limpa o campo de busca
        this.searchInput.value = '';
        this.hideResults();
    }
    
    removeItem(itemId) {
        this.selectedItems.delete(itemId);
        this.renderSelectedItems();
        this.updateHiddenInputs();
    }
    
    renderSelectedItems() {
        if (this.selectedItems.size === 0) {
            this.selectedContainer.innerHTML = '<p class="text-muted mb-0"><i class="fas fa-info-circle me-2"></i>Nenhum líder selecionado</p>';
            return;
        }
        
        const items = Array.from(this.selectedItems.values()).map(item => `
            <div class="badge bg-primary me-2 mb-2 d-inline-flex align-items-center" style="font-size: 0.9em;">
                <span class="me-2">${item.nome}</span>
                <button type="button" 
                        class="btn btn-sm text-white remove-selected-item border-0 p-0" 
                        data-item-id="${item.id}"
                        style="background: transparent; font-size: 1.2em; line-height: 1;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        this.selectedContainer.innerHTML = items;
    }
    
    updateHiddenInputs() {
        // Remove todos os inputs hidden existentes
        this.hiddenContainer.innerHTML = '';
        
        // Cria novos inputs para cada item selecionado
        this.selectedItems.forEach(item => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = this.fieldName;
            input.value = item.id;
            input.dataset.nome = item.nome;
            input.dataset.doc = item.doc;
            this.hiddenContainer.appendChild(input);
        });
    }
}

// Disponibiliza globalmente
window.MultipleAutocompleteField = MultipleAutocompleteField;