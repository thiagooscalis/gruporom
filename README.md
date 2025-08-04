# Grupo ROM - Sistema de Gestão Empresarial

Sistema web Django para gerenciamento empresarial com autenticação baseada em grupos.

## Tecnologias

- Django 5.2
- Bootstrap 5 + HTMX
- PostgreSQL
- Python 3.11+

## Instalação

```bash
# Dependências
uv install
npm install

# Build assets
npm run build

# Migrações
uv run manage.py migrate

# Criar admin
uv run manage.py seed

# Executar
uv run manage.py runserver
```
