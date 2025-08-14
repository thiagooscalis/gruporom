import * as bootstrap from 'bootstrap';
import htmx from 'htmx.org';
import '@fortawesome/fontawesome-free/css/all.css';
import './autocomplete.js';
import './multiple-autocomplete.js';
import './masks.js';

// Make htmx available globally
window.htmx = htmx;
window.bootstrap = bootstrap

// Função global para gerenciar modais
window.modalUtils = {
    /**
     * Fecha um modal e opcionalmente recarrega a página ou redireciona
     * @param {string} modalId - ID do modal (sem #)
     * @param {string} redirectUrl - URL para redirecionar (opcional)
     * @param {boolean} reload - Se deve recarregar a página (padrão: true)
     */
    closeAndReload: function(modalId, redirectUrl = null, reload = true) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
        
        if (redirectUrl) {
            window.location.href = redirectUrl;
        } else if (reload) {
            window.location.reload();
        }
    },
    
    /**
     * Fecha um modal específico sem recarregar
     * @param {string} modalId - ID do modal (sem #)
     */
    close: function(modalId) {
        this.closeAndReload(modalId, null, false);
    },
    
    /**
     * Fecha todos os modais abertos
     */
    closeAll: function() {
        document.querySelectorAll('.modal.show').forEach(function(modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
                modal.hide();
            }
        });
    },
    
    /**
     * Gera script HTML para fechar modal e recarregar (para views Django)
     * @param {string} modalId - ID do modal
     * @param {string} redirectUrl - URL opcional para redirecionamento
     */
    generateCloseScript: function(modalId, redirectUrl = null) {
        const action = redirectUrl 
            ? `window.location.href = '${redirectUrl}';`
            : 'window.location.reload();';
            
        return `
            <script>
                window.modalUtils.closeAndReload('${modalId}', ${redirectUrl ? `'${redirectUrl}'` : 'null'});
            </script>
        `;
    }
};

// Initialize Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap should initialize automatically when imported as a complete package
    // Manual initialization is only needed for dynamic content
});
