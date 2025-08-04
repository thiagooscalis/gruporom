import * as bootstrap from 'bootstrap';
import '@popperjs/core';
import htmx from 'htmx.org';
import '@fortawesome/fontawesome-free/css/all.css';
import './autocomplete.js';

// Make libraries available globally
window.bootstrap = bootstrap;
window.htmx = htmx;

// Initialize Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize all popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
});