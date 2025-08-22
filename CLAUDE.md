# Projeto Grupo ROM - Sistema Empresarial

## Stack Tecnológico
- **Backend**: Django 5.1 + PostgreSQL/SQLite
- **Frontend**: Tailwind CSS v4 + Alpine.js + HTMX + Heroicons
- **Build**: Parcel.js + PostCSS
- **Autenticação**: Custom User Model (AbstractBaseUser)
- **Design System**: Cores da marca (#d3a156)

## Estrutura Principal
```
gruporom/
├── config/          # Configurações Django
├── core/
│   ├── assets/      # JS/CSS fonte (Alpine, HTMX, máscaras)
│   ├── models/      # 23 models (Pessoa, Usuario, WhatsApp, Turismo)
│   ├── templates/   # Templates com componentes reutilizáveis
│   ├── urls/        # URLs organizadas por área
│   └── views/       # Views FBV com decorators
├── static/          # Assets compilados
└── package.json     # Dependências Node.js
```

## Comandos Essenciais
```bash
# Setup inicial
uv install && npm install && npm run build
uv run manage.py migrate
uv run manage.py seed  # Cria admin: thiago/admin123

# Desenvolvimento
uv run manage.py runserver
npm run dev  # Watch mode para assets

# Testes (247 implementados)
./test.sh
```

## Áreas do Sistema

### 1. Administração (`/administracao/`)
- Dashboard com estatísticas
- CRUD completo: Pessoas, Usuários, Fornecedores, Colaboradores
- Gestão WhatsApp Business (contas, templates)
- Sistema de países (193 países ISO-2)

### 2. Comercial (`/comercial/`)
- Atendimento WhatsApp com fila de conversas
- Chat individual com verificação janela 24h
- Sistema de templates para reativação
- Suporte completo a mídias (imagem, vídeo, áudio, documento)

### 3. Operacional (`/operacional/`)
- Gestão de caravanas e turismo com sistema de abas
- Toggle ativo/inativo, autocomplete para responsáveis/líderes
- 15 models interconectados (Voos, Hotéis, Bloqueios, etc)

### 4. Promotor (`/promotor/`)
- Dashboard específico para promotores
- Cadastro multi-step de caravanas

## Padrões de Desenvolvimento

### Frontend
- **Componentes Base**: `modal_form_base.html`, `modal_delete_base.html`
- **Máscaras**: CPF, CNPJ, Telefone, CEP, Passaporte
- **Paginação**: "Carregar mais" com HTMX (20 itens/página)
- **Autocomplete**: Sistema AJAX reutilizável
- **Breadcrumbs**: Sistema padronizado com Heroicons

### Backend
- **Views**: Function-Based com `@login_required` e `@user_passes_test`
- **Grupos**: Administração, Comercial, Operacional, Promotor
- **ForeignKeys**: Sempre com `on_delete=models.PROTECT`
- **Segurança**: CSRF, LoginRequiredMiddleware, campos criptografados

### Padrão HTMX para Listagens
```python
# View
if request.headers.get('HX-Request'):
    if request.GET.get('load_more'):
        return render(request, 'partial_linhas.html', context)
    return render(request, 'partial_lista.html', context)
```

### Padrão de Modal Reutilizável
```django
{% extends "components/modal_form_base.html" %}
{% block modal_title %}Título{% endblock %}
{% block form_attributes %}hx-post="{% url 'url' %}"{% endblock %}
{% block modal_content %}<!-- Conteúdo -->{% endblock %}
```

## WhatsApp Business Integration
- **Meta API**: Envio de mensagens e templates
- **Webhook**: Recebimento automático de mensagens
- **Janela 24h**: Verificação automática com fallback para templates
- **Mídias S3**: URLs assinadas para segurança
- **Mock Mode**: Desenvolvimento sem API real (DEBUG=True)

## Models Principais (23 total)

### Pessoas e Autenticação
- `Pessoa`: CPF/CNPJ, endereço, contatos
- `Usuario`: Custom user com grupos
- `Colaborador`, `Fornecedor`, `Cargo`, `Turno`

### WhatsApp (6 models)
- `WhatsAppAccount`: Contas com tokens criptografados
- `WhatsAppConversation`: Gestão de atendimento
- `WhatsAppMessage`, `WhatsAppTemplate`, `WhatsAppMedia`

### Turismo (15 models)
- `Caravana`, `Bloqueio`, `Passageiro`, `Voo`
- `Hotel`, `Aeroporto`, `CiaArea`, `Pais`, `Cidade`
- `DiaRoteiro`, `Incluso`, `Extra`, `Tarefa`, `Nota`

## URLs Principais
- `/` - Redirecionamento por grupo
- `/administracao/` - Área administrativa
- `/comercial/` - Área comercial
- `/operacional/` - Área operacional
- `/promotor/` - Área promotor
- `/webhook/whatsapp/{id}/` - Webhook WhatsApp

## Status do Projeto
✅ **Sistema em produção** com 4 áreas operacionais completas
✅ **247 testes** implementados com cobertura completa
✅ **WhatsApp Business** integrado com atendimento comercial
✅ **Design System** unificado com Tailwind + Alpine.js
✅ **Área Operacional** padronizada (modal, cores, breadcrumbs)
✅ **Arquitetura escalável** pronta para novos módulos

## Últimas Atualizações (Janeiro 2025)
- **🎯 Área Operacional**: Dashboard e caravanas com design system padronizado
- **📋 Página de Detalhes**: Sistema de abas (Visão Geral, Detalhes, Bloqueios) com layout colapsável
- **🔧 Autocomplete Fields**: Responsável e líderes com busca AJAX reutilizável
- **⚡ Status de Caravanas**: Toggle ativo/inativo via HTMX, padrão inativo ao criar
- **🎨 UX Melhorada**: Breadcrumbs, transições suaves, estados visuais claros

---
**Última atualização**: Janeiro 2025