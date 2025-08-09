// Máscaras de entrada usando IMask
import IMask from 'imask';

// Aplicar máscara baseada no tipo de documento
function applyDocMask(docInput, tipoDocSelect) {
    if (!docInput || !tipoDocSelect) return;
    
    let mask;
    
    const applyMask = () => {
        const tipoDoc = tipoDocSelect.value;
        
        // Destruir máscara anterior se existir
        if (docInput._imask) {
            docInput._imask.destroy();
            delete docInput._imask;
        }
        
        // Aplicar máscara baseada no tipo
        if (tipoDoc === 'CPF') {
            mask = IMask(docInput, {
                mask: '000.000.000-00',
                placeholder: 'CPF'
            });
        } else if (tipoDoc === 'CNPJ') {
            mask = IMask(docInput, {
                mask: '00.000.000/0000-00',
                placeholder: 'CNPJ'
            });
        } else if (tipoDoc === 'Passaporte') {
            // Máscara para passaportes - aceita vários formatos
            mask = IMask(docInput, {
                mask: [
                    // Formato brasileiro: XX000000 (2 letras + 6 dígitos)
                    {
                        mask: 'aa000000',
                        definitions: {
                            'a': /[A-Za-z]/
                        }
                    },
                    // Formato americano: 000000000 (9 dígitos)
                    {
                        mask: '000000000'
                    },
                    // Formato europeu: a0000000 ou aa0000000 (1-2 letras + 6-7 dígitos)
                    {
                        mask: 'aa0000000',
                        definitions: {
                            'a': /[A-Za-z]/
                        }
                    },
                    // Formato genérico: até 12 caracteres alfanuméricos
                    {
                        mask: /^[A-Za-z0-9]{1,12}$/
                    }
                ],
                placeholder: 'Passaporte'
            });
        } else {
            // Para outros tipos (RG, etc.), máscara genérica mais flexível
            mask = IMask(docInput, {
                mask: /^[A-Za-z0-9\-\.\/\s]{1,20}$/,
                placeholder: 'Documento'
            });
        }
        
        // Salvar referência da máscara
        docInput._imask = mask;
    };
    
    // Aplicar máscara inicial
    applyMask();
    
    // Reaplica máscara quando tipo de documento muda
    tipoDocSelect.addEventListener('change', applyMask);
}

// Inicializar máscaras em formulários
function initDocumentMasks() {
    // Para todos os formulários com campos tipo_doc e doc
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const tipoDocSelect = form.querySelector('select[name="tipo_doc"]');
        const docInput = form.querySelector('input[name="doc"]');
        
        if (tipoDocSelect && docInput) {
            applyDocMask(docInput, tipoDocSelect);
        }
    });
}

// Aplicar máscara de telefone dinâmica baseada no DDI
function applyPhoneMask(telefoneInput, ddiInput) {
    if (!telefoneInput) return;
    
    function updateMask() {
        const ddi = ddiInput ? ddiInput.value : '55';
        
        // Destruir máscara anterior se existir
        if (telefoneInput._imask) {
            telefoneInput._imask.destroy();
        }
        
        if (ddi === '55') {
            // Brasil: celular (9xxxx-xxxx) ou fixo (xxxx-xxxx)
            telefoneInput._imask = IMask(telefoneInput, {
                mask: [
                    {
                        mask: '00000-0000',
                        startsWith: '9',
                        country: 'Brasil'
                    },
                    {
                        mask: '0000-0000',
                        startsWith: '',
                        country: 'Brasil'
                    }
                ]
            });
        } else {
            // Outros países: sem máscara
            telefoneInput._imask = null;
        }
    }
    
    // Aplicar máscara inicial
    updateMask();
    
    // Escutar mudanças no DDI
    if (ddiInput) {
        ddiInput.addEventListener('input', updateMask);
        ddiInput.addEventListener('change', updateMask);
    }
}

// Aplicar máscara de telefone (versão antiga - manter compatibilidade)
function initPhoneMasks() {
    const phoneInputs = document.querySelectorAll('input[name="telefone"]');
    
    phoneInputs.forEach(input => {
        IMask(input, {
            mask: [
                {
                    mask: '(00) 0000-0000',
                    startsWith: '',
                    country: 'Brasil'
                },
                {
                    mask: '(00) 00000-0000',
                    startsWith: '',
                    country: 'Brasil'
                }
            ]
        });
    });
}

// Inicializar máscaras de telefone para campos múltiplos
function initMultiplePhoneMasks() {
    // Aplicar em formulários de pessoa com múltiplos telefones
    for (let i = 1; i <= 3; i++) {
        const telefoneInput = document.getElementById(`id_telefone${i}`);
        const ddiInput = document.getElementById(`id_ddi${i}`);
        
        if (telefoneInput) {
            applyPhoneMask(telefoneInput, ddiInput);
        }
    }
}

// Aplicar máscara de CEP
function initCepMasks() {
    const cepInputs = document.querySelectorAll('input[name="cep"]');
    
    cepInputs.forEach(input => {
        IMask(input, {
            mask: '00000-000'
        });
    });
}

// Inicializar todas as máscaras
function initAllMasks() {
    initDocumentMasks();
    initPhoneMasks();
    initMultiplePhoneMasks();
    initCepMasks();
}

// Exportar funções
export {
    applyDocMask,
    applyPhoneMask,
    initDocumentMasks,
    initPhoneMasks,
    initMultiplePhoneMasks,
    initCepMasks,
    initAllMasks
};

// Auto-inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', initAllMasks);

// Reinicializar máscaras quando conteúdo HTMX for carregado
document.addEventListener('htmx:afterSwap', initAllMasks);
document.addEventListener('htmx:afterSettle', initAllMasks);