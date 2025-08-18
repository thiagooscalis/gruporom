# Projeto Grupo ROM - Sistema Empresarial Completo

## Resumo do Projeto
Sistema web Django para gerenciamento empresarial completo com autenticação baseada em grupos, interface responsiva Tailwind CSS, módulos CRUD funcionais para gestão de pessoas, colaboradores, fornecedores, câmbio e WhatsApp Business integrado. Sistema inclui máscaras de entrada inteligentes, modais HTMX, autocomplete avançado, Alpine.js para interatividade e segurança robusta.

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
│   │   ├── app.js           # Alpine.js, HTMX, Máscaras
│   │   ├── autocomplete.js  # Sistema de autocomplete reutilizável
│   │   ├── masks.js         # Máscaras de entrada (CPF, CNPJ, Passaporte, Telefone)
│   │   └── tailwind.css     # Tailwind CSS com configurações customizadas
│   ├── choices.py           # Choices centralizados (TIPO_DOC, SEXO)
│   ├── managers/
│   │   └── usuario.py       # UsuarioManager customizado
│   ├── models/
│   │   ├── pessoa.py        # Model Pessoa (dados pessoais)
│   │   └── usuario.py       # Model Usuario (AbstractBaseUser)
│   ├── data/
│   │   └── paises.json      # Base de dados com 193 países (nome + ISO-2)
│   ├── seeds/
│   │   ├── usuario.py       # Seeder para criar usuário admin
│   │   ├── whatsapp.py      # Seeder para dados de teste WhatsApp
│   │   └── pais.py          # Seeder otimizado para popular países
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
├── static/                  # Assets compilados (Tailwind CSS, Heroicons)
└── package.json            # Dependências Node.js
```

### 🎨 Frontend e Styling
- **Framework CSS**: Tailwind CSS com classes utilitárias e componentes customizados
- **JavaScript Reativo**: Alpine.js para interatividade e gerenciamento de estado
- **Ícones**: Heroicons (SVG inline otimizado)
- **Build**: Parcel.js para compilação de assets + PostCSS para Tailwind
- **Máscaras**: IMask para CPF, CNPJ, Passaporte (multi-formato), Telefone e CEP
- **Autocomplete**: Sistema AJAX reutilizável para busca de pessoas
- **Paginação Moderna**: Sistema "Carregar mais" com HTMX (20 itens/página)
- **Responsividade**: 
  - Desktop: Sidebar fixa com Tailwind classes + conteúdo principal
  - Mobile: Sidebar responsiva com Alpine.js + botão hamburger
- **Modais**: Sistema HTMX + Alpine.js para operações CRUD sem reload
- **Template Tags**: Customizadas para moeda, telefone e documentos
- **⚠️ IMPORTANTE**: Sempre usar componentes Tailwind + Alpine.js para interações. HTMX para requisições assíncronas

### 🔐 Autenticação e Autorização
- **Modelo de Usuário Customizado**: `Usuario` (AbstractBaseUser + PermissionsMixin)
- **Dados Pessoais**: Model `Pessoa` separado com OneToOne para Usuario
- **Grupos**: Sistema baseado em grupos Django (Administração, Comercial, Operacional, Promotor)
- **Redirecionamento**: Usuários redirecionados automaticamente para área do seu grupo
- **Middleware**: LoginRequiredMiddleware ativo (todas as páginas autenticadas)
- **Segurança**: Controle de acesso Django Admin restrito, configurações de segurança robustas
- **Criptografia**: Campos sensíveis (tokens WhatsApp) criptografados com Fernet

### 🗃️ Banco de Dados
- **Modelos Implementados (23 models)**:
  - `Pessoa`: Dados pessoais completos (CPF/CNPJ, endereço, passaporte, etc.)
  - `Usuario`: Autenticação customizada (AbstractBaseUser + PermissionsMixin)
  - `Fornecedor`: Gestão de fornecedores com relacionamento ManyToMany para empresas
  - `Colaborador`: Gestão completa (salário, comissão, turnos, datas admissão/demissão)
  - `Cargo`: Cargos organizacionais com salário base
  - `Turno`: Turnos de trabalho (manhã, tarde, noite)
  - `Funcao`: Funções profissionais com títulos por sexo
  - `Cambio`: Sistema automático de cotação USD/BRL via AwesomeAPI
  - **Sistema de Turismo Completo**:
    - `CiaArea`: Companhias aéreas com código IATA único
    - `Pais`: Países com código ISO de 2 dígitos único (193 países)
    - `Cidade`: Cidades vinculadas a países
    - `Aeroporto`: Aeroportos com código IATA e timezone
    - `Caravana`: Caravanas com empresa, promotor, líderes e configurações
    - `Incluso`: Itens inclusos/não inclusos nos pacotes
    - `Hotel`: Hotéis com endereço e cidade
    - `Bloqueio`: Bloqueios de passagens com países, hotéis e inclusos
    - `Passageiro`: Passageiros vinculados a bloqueios (Guia, VIP, Free)
    - `Voo`: Voos com companhia, aeroportos e horários timezone-aware
    - `DiaRoteiro`: Roteiro dia-a-dia dos bloqueios
    - `Extra`: Extras opcionais com valores
    - `Tarefa`: Tarefas operacionais (Aéreo, Terrestre, Passageiro)
    - `Nota`: Sistema de notas com threads de resposta
  - **WhatsApp Business (6 models)**: 
    - `WhatsAppAccount`: Contas Business com criptografia de tokens
    - `WhatsAppTemplate`: Templates de mensagens com variáveis
    - `WhatsAppConversation`: Gestão de conversas e atendimento
    - `WhatsAppMessage`: Mensagens com suporte a mídias
    - `WhatsAppWebhookLog`: Auditoria de webhooks
    - `WhatsAppMedia`: Armazenamento de mídias
- **Configuração**: PostgreSQL (prod) / SQLite (dev)
- **Localização**: PT-BR, timezone America/Sao_Paulo
- **Padrão ForeignKey**: Todos os relacionamentos ForeignKey usam `on_delete=models.PROTECT` por padrão para evitar exclusões acidentais

### 🛠️ Comandos e Ferramentas
- **Seeder**: `python manage.py seed` - Popula dados iniciais (usuário admin, países, whatsapp)
- **Seeder Específico**: `python manage.py seed --seeder paises` - Popula apenas países (193 países)
- **Build**: `npm run build` - Compila assets
- **Testes**: `./test.sh` - Executa 247 testes com InMemoryStorage (sem warnings)
- **Usuário Admin**: 
  - Username: `thiago`
  - Password: `admin123`
  - Grupos: `Administração`, `Comercial`, `Operacional`, `Promotor`

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
- [x] Tema customizado com Tailwind CSS (cor primária: #d3a156)
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
- [x] **Pais**: Sistema de países com códigos ISO-2 (193 países)
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
- [x] **Paginação Moderna**: Sistema "Carregar mais" com HTMX (20 itens/página)
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
  - [x] Verificação de janela de 24h do WhatsApp antes de enviar mensagens
  - [x] Notificações toast quando fora da janela de 24h
  - [x] Envio de templates para reabrir conversas expiradas
- [x] **Sistema de Mídias Completo**: Visualização robusta de todos os tipos de mídia
  - [x] Imagens com modal HTMX e zoom
  - [x] Vídeos com player HTML5 e fallback de erro
  - [x] Áudios com player customizado e Web Audio API
  - [x] Documentos com preview e download S3
  - [x] URLs S3 assinadas para segurança
  - [x] Tratamento de erro automático com retry
- [x] **Interface de Chat Otimizada**: UX profissional para atendimento
  - [x] Layout responsivo com altura fixa
  - [x] Botão flutuante para ir ao final da conversa
  - [x] Modais HTMX para envio de templates
  - [x] Mock API para ambiente de desenvolvimento
  - [x] Limpeza automática de formulários após envio

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
- [x] **Janela de 24h WhatsApp**: Verificação automática antes de enviar mensagens
- [x] **Templates para Reativação**: Sistema para reabrir conversas expiradas
- [x] **UX Otimizada**: Botão scroll, modais inteligentes, layout responsivo
- [x] **Novo Contato**: Cadastro rápido com validação inteligente de telefone (Brasil/Internacional)

### 8. Sistema Multi-Área
- [x] **Grupos de Acesso**: Administração, Comercial, Operacional, Promotor
- [x] **Menu de Alternância**: Modal para trocar entre áreas rapidamente
- [x] **Context Processor**: Detecção automática da área atual
- [x] **Autorização Granular**: `user_passes_test` para cada área
- [x] **URLs Organizadas**: Estrutura modular por área/funcionalidade

### 9. Sistema de Turismo Empresarial
- [x] **Modelos Relacionais Completos**: 14 models interconectados para gestão de turismo
- [x] **Caravanas e Líderes**: Sistema de caravanas com múltiplos líderes e controle de tipos
- [x] **Bloqueios Inteligentes**: Gestão de bloqueios com países, hotéis, inclusos e extras
- [x] **Controle de Passageiros**: Sistema de passageiros com tipos especiais (Guia, VIP, Free)
- [x] **Gestão de Voos**: Voos completos com companhias, aeroportos e horários timezone-aware
- [x] **Roteiros Detalhados**: Sistema de dias de roteiro organizados por bloqueio
- [x] **Tarefas Operacionais**: Controle de tarefas por categoria (Aéreo, Terrestre, Passageiro)
- [x] **Sistema de Notas**: Comunicação interna com threads de resposta

### 10. Sistema de Testes Completo
- [x] **247 Testes Implementados**: Cobertura completa de todos os models, views e forms
- [x] **InMemoryStorage**: Testes não salvam arquivos no disco
- [x] **Timezone-Aware**: Todos os DateTimeFields com timezone correto
- [x] **Factory-Boy Otimizado**: 14 factories com relacionamentos ManyToMany
- [x] **Zero Warnings**: Configuração limpa sem deprecation warnings
- [x] **Performance Otimizada**: MD5 hasher, cache desabilitado, migrações aceleradas
- [x] **Script Personalizado**: `./test.sh` para execução com configurações corretas

### 11. Administração Avançada
- [x] Dashboard simplificado com estatísticas essenciais
- [x] Controle de acesso granular por grupos
- [x] Configurações de segurança robustas (CSRF, HSTS, CSP)
- [x] Interface administrativa Django restrita

## 🚀 Status Atual: Sistema Empresarial Completo com WhatsApp Business e Mídias

**O projeto está em estado PRODUTIVO COMPLETO** com:
- **4 áreas operacionais**: Administração (gestão) + Comercial (atendimento) + Operacional (turismo) + Promotor (caravanas)
- **WhatsApp Business completo**: Configuração (admin) + Atendimento (comercial) + **Mídias integradas** + **Janela 24h**
- **Sistema de mídias robusto**: Imagens, vídeos, áudios e documentos com S3 e fallback
- **Sistema de turismo empresarial**: 15 models interconectados para gestão completa
- **Sistema de conversas avançado**: Webhook → Fila → Atribuição → Chat individual → **Verificação 24h** → **Templates automáticos**
- **247 testes implementados**: Sistema de testes robusto com InMemoryStorage e cobertura completa
- **UX profissional** com botão scroll, modais inteligentes e layout otimizado
- **Segurança robusta** com criptografia de campos sensíveis e **arquitetura escalável**

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

### Comandos de Testes
```bash
# Executar todos os 247 testes (recomendado)
./test.sh

# Parar no primeiro erro
./test.sh -x

# Executar testes específicos
./test.sh core/tests/test_models.py::CiaAreaModelTest

# Modo verbose
./test.sh -v

# Com cobertura de código
./test.sh --cov=core

# Executar apenas factories
./test.sh core/tests/test_factories.py

# Executar apenas models
./test.sh core/tests/test_models.py

# Método alternativo (manual)
DJANGO_SETTINGS_MODULE=core.test_settings uv run pytest -x
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
- `/comercial/whatsapp/geral/` - Visão gerencial de todas as conversas
- `/comercial/whatsapp/novo-contato/` - Cadastro rápido de novos contatos
- `/comercial/whatsapp/assign/{id}/` - Atribuir conversa ao usuário
- `/comercial/whatsapp/conversation/{id}/` - Interface de chat individual

#### Área Operacional
- `/operacional/` - Dashboard operacional
- `/operacional/caravanas/` - Gestão de caravanas

#### Área Promotor
- `/promotor/` - Dashboard do promotor
- `/promotor/nova-caravana/` - Cadastro multi-step de caravanas

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
- **Paginação Moderna**: Sistema "Carregar mais" com HTMX em todas as listagens
- **Busca Otimizada**: Índices Q() para múltiplos campos
- **Asset Bundling**: CSS/JS otimizados via Parcel + PostCSS
- **Cache de Templates**: Rendering otimizado

### 📋 Área Promotor
- [x] **Dashboard Promotor**: Interface dedicada para promotores
- [x] **Cadastro de Caravanas**: Sistema multi-step para criação de caravanas
- [x] **Gestão de Caravanas**: Listagem e edição de caravanas próprias
- [x] **Controle de Acesso**: Promotores só veem suas próprias caravanas

### 📋 Padrão de Paginação "Carregar Mais"
**Implementação HTMX para todas as listagens do sistema:**

#### Estrutura de Templates:
- **Template Principal**: `lista.html` com formulário de busca e include do partial
- **Template Partial**: `partial_lista.html` com tabela completa + botão "Carregar mais"
- **Template Linhas**: `partial_linhas.html` com apenas `<tr>` para append incremental

#### View Pattern:
```python
# Paginação padrão: 20 itens/página
paginator = Paginator(objetos, 20)
page_obj = paginator.get_page(page_number)

context = {
    'page_obj': page_obj,
    'search': search,
    'filtros': filtros,
    'restantes': page_obj.paginator.count - page_obj.end_index() if page_obj else 0,
}

# HTMX Detection
if request.headers.get('HX-Request'):
    if request.GET.get('load_more'):
        return render(request, 'app/partial_linhas.html', context)  # Append
    else:
        return render(request, 'app/partial_lista.html', context)   # Replace
```

#### Template HTMX:
```html
<!-- Formulário com HTMX -->
<form hx-get="{% url 'lista' %}" hx-target="#lista-container" 
      hx-swap="outerHTML" hx-push-url="true" hx-trigger="submit">

<!-- Tabela com ID para append -->
<tbody id="objetos-tbody">

<!-- Botão Carregar Mais -->
<button hx-get="?page={{ page_obj.next_page_number }}&load_more=1"
        hx-target="#objetos-tbody" hx-swap="beforeend">
    Carregar mais ({{ restantes }} restantes)
</button>
```

#### Funcionalidades:
- ✅ **HTMX Incremental**: Adiciona linhas sem reload
- ✅ **URL Atualizada**: `hx-push-url="true"` para bookmarks
- ✅ **Filtros Preservados**: Mantém busca e filtros na paginação
- ✅ **Contador Dinâmico**: Mostra quantos itens restam
- ✅ **Auto-hide**: Botão desaparece na última página
- ✅ **Mobile UX**: Experiência otimizada para dispositivos móveis

### Estrutura de URLs Escalável
- URLs organizadas por módulo com namespaces
- Padrão RESTful para operações CRUD
- Fácil adição de novos módulos empresariais

---

**Última atualização**: 18/08/2025  
**Status**: Sistema empresarial completo com WhatsApp Business integrado, sistema robusto de mídias, paginação HTMX moderna, janela 24h automática e multi-área operacional  
**Stack Frontend**: Tailwind CSS + Alpine.js + HTMX + Heroicons  
**Módulos**: 23 modelos de dados (Pessoa, Usuario, Fornecedor, Colaborador, Cargo, Turno, Funcao, Cambio, Pais, WhatsApp [6 models], Turismo [15 models]), sistema completo de mídias (imagens, vídeos, áudios, documentos), URLs S3 assinadas, verificação de janela 24h, validação inteligente de telefones, UX otimizada

## 🆕 Últimas Atualizações

### Agosto 2025 - Sistema de Países e Seeds Otimizados
- **🌍 Base de Dados Completa**: 193 países com nomes em português e códigos ISO-2
- **📁 Arquivo JSON Estruturado**: `/core/data/paises.json` com formato padronizado
- **⚡ Seeder Otimizado**: 
  - Verificação eficiente com 1 consulta vs 193 individuais
  - Bulk insert para máxima performance
  - Zero duplicatas com verificação por conjunto de ISOs
- **🔧 Integração Command Seed**: 
  - `python manage.py seed --seeder paises` - Seeder específico
  - `python manage.py seed` - Inclui países no seeder geral
- **📊 Feedback Visual**: Emojis e contadores informativos
- **🚀 Pronto para Uso**: Model Pais disponível para formulários Django

### Agosto 2025 - Paginação Moderna "Carregar Mais"
- **📱 UX Moderna**: Substituição da paginação tradicional por botão "Carregar mais" com HTMX
- **⚡ Performance HTMX**: 
  - Filtros via botão (sem auto-trigger)
  - Carregamento incremental sem reload de página
  - URL atualizada com `hx-push-url="true"`
- **🔧 Padrão Reutilizável**: Estrutura padronizada para todas as listagens
  - `partial_lista.html` → Tabela completa + botão carregar mais
  - `partial_linhas.html` → Apenas `<tr>` para append incremental
  - Context com `restantes` calculado na view
- **📊 Contador Dinâmico**: Mostra quantos registros restam para carregar
- **🎯 Auto-hide**: Botão desaparece automaticamente na última página
- **🧪 Testes Completos**: 7 testes automatizados para validar funcionalidade
- **📋 Padronização**: Aplicado inicialmente em Pessoas, pronto para expansão

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

### Agosto 2025 - Sistema Completo de Mídias WhatsApp
- **📱 Visualização Completa de Mídias**: Sistema robusto para exibir todos os tipos de mídia do WhatsApp
  - **🖼️ Imagens**: Modal HTMX com visualização expandida e URLs S3 assinadas
  - **🎵 Áudio**: Player personalizado com Web Audio API para demonstração
  - **🎬 Vídeos**: Player nativo HTML5 com fallback inteligente para erros
  - **📄 Documentos**: Preview com download direto via URLs assinadas
- **🔐 URLs S3 Assinadas**: Método `get_signed_media_url()` para acesso seguro a mídias privadas
- **⚡ Tratamento de Erros Robusto**: Sistema de fallback automático quando mídias falham ao carregar
  - Logs detalhados de debug no console
  - Mensagens de erro amigáveis com opção "Tentar novamente"
  - Substituição automática de players com erro por mensagens informativas
- **🎯 Estrutura de Templates Otimizada**: Lógica reorganizada para detectar corretamente tipos de mídia
- **📂 Organização S3 Profissional**: Estrutura hierárquica `media/whatsapp/tipo/ano/mes/dia/arquivo`
- **🚀 Integração HTMX**: Modais carregados dinamicamente com JavaScript local para máxima compatibilidade

### Agosto 2025 - Validação Inteligente de Telefones Internacionais
- **🌍 Validação por DDI**: Sistema inteligente que ajusta validação baseado no país
  - Brasil (DDI 55): Aceita apenas 8 ou 9 dígitos para o número
  - Internacional (outros DDIs): Aceita entre 5 e 15 dígitos
- **📱 Formulário NovoContatoForm**: Atualizado com validação contextual
- **✅ Melhor UX**: Mensagens de erro específicas por tipo de número

### Agosto 2025 - Interface de Chat Profissional e Janela 24h
- **⏰ Verificação Automática de Janela 24h**: Sistema inteligente que verifica se a conversa está dentro da janela de 24h do WhatsApp
  - Método `is_within_24h_window()` no model WhatsAppConversation
  - Endpoint AJAX `/comercial/whatsapp/check-24h-window/` para verificação em tempo real
  - Bloqueio automático de mensagens quando fora da janela com toast informativo
  - Redirecionamento para envio de templates quando necessário reativar conversa
- **🎯 UX Otimizada para Atendimento**: Interface profissional com foco na experiência do atendente
  - Layout responsivo com altura fixa para evitar scroll indesejado
  - Botão flutuante inteligente para ir ao final da conversa (aparece/desaparece conforme scroll)
  - Modais HTMX para envio de templates com limpeza automática após uso
  - Sistema de eventos HTMX (`afterSwap`) para sincronização automática de componentes
- **🛠️ Ambiente de Desenvolvimento**: Mocks completos para desenvolvimento sem API real
  - Mock responses para WhatsApp API em modo DEBUG
  - Simulação realística de envio de mensagens e templates
  - Logs coloridos e informativos para debug

### Dezembro 2024 - Migração para Tailwind CSS + Alpine.js
- **🎨 Novo Stack Frontend**: Migração completa de Bootstrap 5 + FontAwesome para Tailwind CSS + Alpine.js + Heroicons
- **⚡ Performance Melhorada**: CSS utilitário com purge automático, apenas classes utilizadas
- **🔧 Interatividade Moderna**: Alpine.js para componentes reativos sem framework pesado
- **🎯 Developer Experience**: Classes utilitárias intuitivas, componentes reutilizáveis
- **📦 Build Otimizado**: PostCSS integrado para processamento eficiente do Tailwind
- **🎨 Design System**: Mantida cor primária #d3a156 com classes customizadas Tailwind
- **📱 Responsividade Aprimorada**: Sistema de breakpoints do Tailwind (sm, md, lg, xl, 2xl)
- **🚀 Componentes Alpine**: Modais, dropdowns, sidebars com x-data e x-show