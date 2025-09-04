import * as bootstrap from 'bootstrap';
import htmx from 'htmx.org';
import '@fortawesome/fontawesome-free/css/all.css';
import './autocomplete.js';
import './multiple-autocomplete.js';
import './masks.js';
import './cep.js';

// Make htmx available globally
window.htmx = htmx;
window.bootstrap = bootstrap

// Initialize Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap should initialize automatically when imported as a complete package
    // Manual initialization is only needed for dynamic content
});
