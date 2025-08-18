/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './core/templates/**/*.html',
    './core/assets/**/*.js',
    './core/static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#d3a156',
        'sidebar': '#333333',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}