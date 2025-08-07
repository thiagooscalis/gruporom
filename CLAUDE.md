# Projeto Grupo ROM - Sistema Empresarial Completo

## Resumo do Projeto
Sistema web Django para gerenciamento empresarial completo com autenticação baseada em grupos, interface responsiva Bootstrap 5, módulos CRUD funcionais para gestão de pessoas, colaboradores, fornecedores, câmbio e WhatsApp Business integrado. Sistema inclui máscaras de entrada inteligentes, modais HTMX, autocomplete avançado e segurança robusta.

## Estrutura do Projeto Atual

### 🗂️ Estrutura de Arquivos
```
gruporom/
├── config/
│   ├── settings.py           # Configurações Django (PT-BR, PostgreSQL, custom user)
│   ├── urls.py              # URLs principais com auth e administração
│   └── wsgi.py
├── core/
│   ├── assets/
│   │   ├── app.js           # Bootstrap, HTMX, FontAwesome, Máscaras
│   │   ├── autocomplete.js  # Sistema de autocomplete reutilizável
│   │   ├── masks.js         # Máscaras de entrada (CPF, CNPJ, Passaporte, Telefone)
│   │   └── style.scss       # Bootstrap customizado (cor primária: #d3a156)
│   ├── choices.py           # Choices centralizados (TIPO_DOC, SEXO)
│   ├── managers/
│   │   └── usuario.py       # UsuarioManager customizado
│   ├── models/
│   │   ├── pessoa.py        # Model Pessoa (dados pessoais)
│   │   └── usuario.py       # Model Usuario (AbstractBaseUser)
│   ├── seeds/
│   │   └── usuario.py       # Seeder para criar usuário admin
│   ├── management/commands/
│   │   └── seed.py          # Command para executar seeders
│   ├── templates/
│   │   ├── base.html        # Template base com navbar e sidebar
│   │   ├── includes/
│   │   │   └── aside.html   # Sidebar responsivo (desktop/mobile offcanvas)
│   │   ├── registration/
│   │   │   ├── base.html    # Layout de login
│   │   │   └── login.html   # Formulário de login com crispy forms
│   │   └── administracao/
│   │       └── home.html    # Dashboard administrativo
│   ├── urls/
│   │   ├── base.py          # URL de redirecionamento por grupo
│   │   └── administracao/
│   │       ├── __init__.py  # URLs da administração
│   │       └── base.py      # Home da administração
│   └── views/
│       ├── base.py          # RedirectToGroupView
│       └── administracao/
│           └── base.py      # Views da administração
├── static/                  # Assets compilados (Bootstrap, FontAwesome)
└── package.json            # Dependências Node.js
```

### 🎨 Frontend e Styling
- **Framework CSS**: Bootstrap 5 com cor primária personalizada (#d3a156 - cor do logo)
- **Ícones**: FontAwesome 6 (importado via CSS)
- **Build**: Parcel.js para compilação de assets
- **Máscaras**: IMask para CPF, CNPJ, Passaporte (multi-formato), Telefone e CEP
- **Autocomplete**: Sistema AJAX reutilizável para busca de pessoas
- **Responsividade**: 
  - Desktop: Sidebar fixa (#333333) + conteúdo principal
  - Mobile: Offcanvas sidebar + botão hamburger
- **Modais**: Sistema HTMX para operações CRUD sem reload

### 🔐 Autenticação e Autorização
- **Modelo de Usuário Customizado**: `Usuario` (AbstractBaseUser + PermissionsMixin)
- **Dados Pessoais**: Model `Pessoa` separado com OneToOne para Usuario
- **Grupos**: Sistema baseado em grupos Django (ex: "Administração")
- **Redirecionamento**: Usuários redirecionados automaticamente para área do seu grupo
- **Middleware**: LoginRequiredMiddleware ativo (todas as páginas autenticadas)
- **Segurança**: Controle de acesso Django Admin restrito, configurações de segurança robustas

### 🗃️ Banco de Dados
- **Modelos Implementados**:
  - `Pessoa`: Dados pessoais completos (CPF/CNPJ, endereço, passaporte, etc.)
  - `Usuario`: Autenticação customizada (AbstractBaseUser + PermissionsMixin)
  - `Fornecedor`: Gestão de fornecedores com relacionamento ManyToMany para empresas
  - `Colaborador`: Gestão completa (salário, comissão, turnos, datas admissão/demissão)
  - `Cargo`: Cargos organizacionais com salário base
  - `Turno`: Turnos de trabalho (manhã, tarde, noite)
  - `Cambio`: Sistema automático de cotação USD/BRL via AwesomeAPI
  - **WhatsApp Business**: Contas, templates, mensagens e integração API
- **Configuração**: PostgreSQL (prod) / SQLite (dev)
- **Localização**: PT-BR, timezone America/Sao_Paulo

### 🛠️ Comandos e Ferramentas
- **Seeder**: `python manage.py seed` - Cria usuário admin padrão
- **Build**: `npm run build` - Compila assets
- **Usuário Admin**: 
  - Username: `thiago`
  - Password: `admin123`
  - Grupo: `Administração`

## ✅ Funcionalidades Implementadas

### 1. Sistema de Autenticação Completo
- [x] Login customizado com crispy forms
- [x] Logout funcional com modal de confirmação
- [x] Redirecionamento baseado em grupos
- [x] Usuário admin criado via seeder
- [x] Sistema de alteração de senhas
- [x] Middleware de autenticação obrigatória
- [x] Controle de acesso Django Admin (apenas super admin)

### 2. Interface de Usuário Profissional
- [x] Layout responsivo com sidebar (#333333) e offcanvas
- [x] Navbar com informações do usuário logado e câmbio USD/BRL
- [x] Logo personalizado do Grupo ROM
- [x] Dashboard administrativo simplificado com estatísticas essenciais
- [x] Breadcrumbs de navegação em todas as páginas
- [x] Floating action buttons com estilo consistente (texto branco)
- [x] Sistema de mensagens e alertas integrado
- [x] Tema customizado (#d3a156) com Bootstrap 5
- [x] Componentes modais para todas as operações CRUD
- [x] Sistema de mensagens e alertas
- [x] Breadcrumbs de navegação

### 3. Modelos de Dados Empresariais
- [x] **Pessoa**: Dados completos (CPF/CNPJ, endereços, contatos)
- [x] **Usuario**: Sistema customizado de autenticação
- [x] **Fornecedor**: Gestão com categorização por tipo de empresa
- [x] **Colaborador**: Controle completo (salários, comissões, turnos)
- [x] **Cargo**: Estrutura organizacional com salários base
- [x] **Turno**: Gestão de horários de trabalho
- [x] **Cambio**: Cotação automática USD/BRL via API externa
- [x] **WhatsAppConversation**: Gestão de conversas comerciais com atendentes
- [x] Choices centralizados e validações robustas
- [x] Relacionamentos otimizados com ForeignKey/ManyToMany

### 4. Sistema CRUD Completo
- [x] **Pessoas**: Listagem, busca, criação, edição, exclusão com validações robustas
- [x] **Usuários**: Gestão completa com grupos, autocomplete de pessoas e modal de criação rápida
- [x] **Fornecedores**: CRUD com relacionamento a empresas
- [x] **Colaboradores**: Gestão RH completa
- [x] **Cargos**: Estrutura organizacional
- [x] **Turnos**: Controle de horários
- [x] Paginação em todas as listagens (20 itens/página)
- [x] Sistema de busca integrado com autocomplete AJAX
- [x] Validações frontend (máscaras) e backend
- [x] Proteção contra exclusão de registros relacionados
- [x] Modal de criação rápida de pessoa no cadastro de usuários

### 5. WhatsApp Business Integrado
- [x] **Contas WhatsApp**: Gestão completa de contas Business com cards quadrados
- [x] **Templates**: Sistema de templates de mensagem com preview e validação
- [x] **Dashboard WhatsApp**: Interface limpa com contas ativas e últimos templates
- [x] **API Integration**: Configuração completa com Meta/Facebook API
- [x] **Guia Integrado**: Modal "Como obter?" com tutorial passo-a-passo para credenciais
- [x] **Webhook Support**: URLs automáticas e configuração de verify tokens
- [x] **Teste de Conexão**: Validação de credenciais e conectividade da API
- [x] **Interface Responsiva**: Cards organizados, modais HTMX e navegação intuitiva
- [x] **Atendimento Comercial**: Sistema completo de atendimento ao cliente
  - [x] Dashboard com fila de conversas aguardando
  - [x] Sistema de atribuição de atendente
  - [x] Interface de chat para atendimento
  - [x] Espelhamento automático via webhook
  - [x] Controle de status de conversas

### 6. Máscaras de Entrada Inteligentes
- [x] **CPF**: Formatação automática `000.000.000-00`
- [x] **CNPJ**: Formatação automática `00.000.000/0000-00`
- [x] **Passaporte**: Multi-formato (Brasileiro, Americano, Europeu, Genérico)
- [x] **Telefone**: Fixo e celular `(00) 0000-0000` / `(00) 00000-0000`
- [x] **CEP**: Formatação `00000-000`
- [x] **Detecção automática**: Máscara muda conforme tipo de documento selecionado
- [x] **Compatibilidade HTMX**: Reinicialização automática em conteúdo dinâmico

### 7. Área Comercial Completa
- [x] **Dashboard Comercial**: Interface dedicada para equipe de vendas
- [x] **WhatsApp Atendimento**: Fila de conversas aguardando atendimento
- [x] **Sistema de Atribuição**: Atendente assume conversa com um clique
- [x] **Interface de Chat**: Atendimento individual com histórico completo
- [x] **Controle de Status**: pending → assigned → in_progress → resolved
- [x] **Espelhamento Automático**: Webhook cria conversas automaticamente
- [x] **Menu Lateral Específico**: Navegação otimizada para área comercial
- [x] **Estatísticas em Tempo Real**: Conversas pendentes, minhas conversas

### 8. Sistema Multi-Área
- [x] **Grupos de Acesso**: Administração, Comercial (expansível)
- [x] **Menu de Alternância**: Modal para trocar entre áreas rapidamente
- [x] **Context Processor**: Detecção automática da área atual
- [x] **Autorização Granular**: `user_passes_test` para cada área
- [x] **URLs Organizadas**: Estrutura modular por área/funcionalidade

### 9. Administração Avançada
- [x] Dashboard simplificado com estatísticas essenciais
- [x] Controle de acesso granular por grupos
- [x] Configurações de segurança robustas (CSRF, HSTS, CSP)
- [x] Interface administrativa Django restrita

## 🚀 Status Atual: Sistema Produtivo Completo Multi-Área

**O projeto está em estado PRODUTIVO COMPLETO** com:
- **2 áreas operacionais**: Administração (gestão) + Comercial (atendimento)
- **WhatsApp Business completo**: Configuração (admin) + Atendimento (comercial)
- **Sistema de conversas**: Webhook → Fila → Atribuição → Chat individual
- **Máscaras inteligentes** e **interface otimizada**
- **Segurança robusta** e **arquitetura escalável**

## 🔮 Próximas Expansões Sugeridas

### Módulos de Negócio
1. **Vendas & Faturamento**: Pedidos, notas fiscais, controle de estoque
2. **Financeiro**: Contas a pagar/receber, fluxo de caixa, relatórios
3. **RH Avançado**: Folha de pagamento, ponto eletrônico, férias
4. **CRM**: Gestão de clientes, oportunidades, pipeline de vendas

### Integrações e APIs
1. **Uploads**: Storage S3/CloudFlare para documentos e fotos
2. **APIs Externas**: Receita Federal, ViaCEP, sistemas bancários
3. **Relatórios**: PDF/Excel exportáveis, dashboards analíticos
4. **Notificações**: Email, SMS, push notifications

### Performance e Escalabilidade
1. **Cache Redis**: Para consultas frequentes e sessões
2. **Background Jobs**: Celery para processamentos pesados
3. **Monitoramento**: Sentry, métricas de performance
4. **Deploy**: Docker, CI/CD, ambientes staging/production

## 🔧 Configuração de Desenvolvimento

### Requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL (opcional, SQLite por padrão)

### Setup Inicial
```bash
# Instalar dependências Python
uv install

# Instalar dependências Node.js
npm install

# Compilar assets
npm run build

# Migrar banco (8 migrações aplicadas)
uv run manage.py migrate

# Popular dados iniciais (usuário admin + grupos)
uv run manage.py seed

# Executar testes (opcional)
uv run manage.py test

# Iniciar servidor de desenvolvimento
uv run manage.py runserver
```

### Comandos de Manutenção
```bash
# Verificar problemas do sistema
uv run manage.py check

# Criar nova migração
uv run manage.py makemigrations

# Ver status das migrações
uv run manage.py showmigrations

# Recompilar assets durante desenvolvimento
npm run dev  # modo watch

# Criar dados de teste WhatsApp (opcional)
uv run python test_whatsapp_flow.py
```

### URLs Principais
- `/` - Redirecionamento automático por grupo
- `/login/` - Página de login responsiva

#### Área Administração
- `/administracao/` - Dashboard administrativo simplificado
- `/administracao/pessoas/` - Gestão de pessoas com autocomplete
- `/administracao/usuarios/` - Gestão de usuários com criação rápida de pessoas
- `/administracao/fornecedores/` - Gestão de fornecedores
- `/administracao/colaboradores/` - Gestão de colaboradores
- `/administracao/cargos/` - Gestão de cargos
- `/administracao/turnos/` - Gestão de turnos
- `/administracao/whatsapp/` - Dashboard WhatsApp Business (configuração)
- `/administracao/whatsapp/accounts/` - Listagem de contas WhatsApp
- `/administracao/whatsapp/account/{id}/templates/` - Templates por conta

#### Área Comercial
- `/comercial/` - Dashboard comercial
- `/comercial/whatsapp/` - Atendimento WhatsApp (fila de conversas)
- `/comercial/whatsapp/assign/{id}/` - Atribuir conversa ao usuário
- `/comercial/whatsapp/conversation/{id}/` - Interface de chat individual

#### Sistema
- `/admin/` - Django Admin nativo (acesso restrito)
- `/webhook/whatsapp/{account_id}/` - Webhook para receber mensagens

## 📝 Observações Técnicas

### Arquitetura do Sistema
- **Padrão MVT Django**: Views baseadas em funções com decorators de segurança
- **Modais HTMX**: Operações CRUD sem reload de página
- **Componentes Reutilizáveis**: Templates modulares e templatetags customizadas
- **Autocomplete Ajax**: Busca dinâmica de pessoas e relacionamentos

### Sistema de Integrações
- **AwesomeAPI**: Cotação automática de câmbio USD/BRL com cache no banco
- **WhatsApp Business API**: Integração completa com Meta/Facebook API
- **Factories**: Geração de dados de teste com Faker
- **Seeds**: População automática de dados iniciais
- **IMask**: Biblioteca para máscaras de entrada inteligentes

### Segurança Implementada
- **CSRF Protection**: Ativo em todos os formulários
- **LoginRequired**: Middleware global
- **Group-based Authorization**: Controle de acesso por grupos
- **Protected Deletion**: Proteção contra exclusão de registros relacionados

### Performance e UX
- **Paginação**: 20 registros por página em todas as listagens
- **Busca Otimizada**: Índices Q() para múltiplos campos
- **Asset Bundling**: CSS/JS otimizados via Parcel
- **Cache de Templates**: Rendering otimizado

### Estrutura de URLs Escalável
- URLs organizadas por módulo com namespaces
- Padrão RESTful para operações CRUD
- Fácil adição de novos módulos empresariais

---

**Última atualização**: 07/08/2025  
**Status**: Sistema empresarial completo com WhatsApp Business integrado, área comercial de atendimento, multi-área e máscaras inteligentes  
**Módulos**: 9+ modelos de dados, 8+ CRUDs funcionais, WhatsApp Business com atendimento comercial completo, sistema de câmbio automático, área comercial funcional

## 🆕 Últimas Atualizações

### Agosto 2025 - Área Comercial e WhatsApp Atendimento
- **🏢 Área Comercial Completa**: Nova área de acesso com grupo "Comercial" e interface dedicada
- **💬 WhatsApp Atendimento Comercial**: Sistema completo de atendimento ao cliente via WhatsApp
  - Dashboard com conversas aguardando atendimento
  - Sistema de atribuição de conversas aos atendentes
  - Interface de chat para atendimento individual
  - Espelhamento automático via webhook (mensagens → conversas)
- **🔄 Modelo WhatsAppConversation**: Gestão de conversas com status, atendente e controle de fluxo
- **🎯 Fluxo Comercial Otimizado**: 
  - Mensagens chegam via webhook → Criam conversas pendentes
  - Comercial visualiza fila de atendimento
  - Clica "Atender" → Conversa é atribuída ao usuário
  - Interface de chat individual para responder cliente
- **🏗️ Arquitetura Padronizada**: Conversão para Function-Based Views (FBVs) com decorators `user_passes_test`
- **🔀 Sistema Multi-Área**: Menu de alternância entre áreas (Administração ↔ Comercial)
- **📊 Context Processor Inteligente**: Detecção automática da área atual baseada em grupos do usuário
- **🧪 Dados de Teste**: Script automatizado para criar conversas de teste