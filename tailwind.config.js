/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './core/templates/**/*.html',
    './core/assets/**/*.js',
    './core/static/**/*.js',
  ],
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}