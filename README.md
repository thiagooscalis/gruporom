# Grupo ROM - Sistema de Gest�o Empresarial

Sistema web Django para gerenciamento empresarial com autentica��o baseada em grupos.

## Tecnologias

- Django 5.2
- Bootstrap 5 + HTMX
- PostgreSQL
- Python 3.11+

## Instala��o

```bash
# Depend�ncias
uv install
npm install

# Build assets
npm run build

# Migra��es
uv run manage.py migrate

# Criar admin
uv run manage.py seed

# Executar
uv run manage.py runserver
```
