// Função para buscar CEP usando a API ViaCEP
function buscarCEP(cepValue) {
    // Remove caracteres não numéricos
    const cep = cepValue.replace(/\D/g, '');
    
    // Valida o CEP
    if (cep.length !== 8) {
        return;
    }
    
    // URL da API ViaCEP
    const url = `https://viacep.com.br/ws/${cep}/json/`;
    
    // Faz a requisição
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (!data.erro) {
                // Preenche os campos do formulário
                preencherEndereco(data);
            } else {
                console.warn('CEP não encontrado');
            }
        })
        .catch(error => {
            console.error('Erro ao buscar CEP:', error);
        });
}

// Função para preencher os campos de endereço
function preencherEndereco(data) {
    // Mapear os campos do ViaCEP para os campos do formulário
    const campos = {
        'endereco': data.logradouro,
        'bairro': data.bairro,
        'cidade': data.localidade,
        'estado': data.uf
    };
    
    // Preencher cada campo
    for (const [campo, valor] of Object.entries(campos)) {
        const element = document.querySelector(`[name="${campo}"]`);
        if (element && valor) {
            element.value = valor;
            
            // Dispara evento de change para atualizar o form
            element.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}

// Inicializar busca de CEP quando o documento estiver pronto
function initCepSearch() {
    // Adiciona listener para campos de CEP
    document.addEventListener('blur', function(event) {
        if (event.target && event.target.name === 'cep') {
            const cepValue = event.target.value;
            if (cepValue) {
                buscarCEP(cepValue);
            }
        }
    }, true);
    
    // Adiciona listener para mudança no campo CEP (para quando o usuário cola o valor)
    document.addEventListener('change', function(event) {
        if (event.target && event.target.name === 'cep') {
            const cepValue = event.target.value;
            if (cepValue && cepValue.replace(/\D/g, '').length === 8) {
                buscarCEP(cepValue);
            }
        }
    }, true);
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCepSearch);
} else {
    initCepSearch();
}

// Exportar funções para uso global
window.buscarCEP = buscarCEP;
window.initCepSearch = initCepSearch;

// Re-inicializar após carregamento HTMX
document.body.addEventListener('htmx:afterSwap', function() {
    initCepSearch();
});

document.body.addEventListener('htmx:afterSettle', function() {
    initCepSearch();
});