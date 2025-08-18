import htmx from 'htmx.org';
import Alpine from 'alpinejs';
import './tailwind.css';
import './autocomplete.js';
import './masks.js';

// Make available globally
window.htmx = htmx;
window.Alpine = Alpine;

// Start Alpine.js
Alpine.start();
