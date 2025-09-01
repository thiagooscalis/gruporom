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
├── static/                  # Assets compilados (Bootstrap, FontAwesome)
└── package.json            # Dependências Node.js
```

### 🎨 Frontend e Styling
- **Framework CSS**: Bootstrap 5 com cor primária personalizada (#d3a156 - cor do logo)
- **Ícones**: FontAwesome 6 (importado via CSS)
- **Build**: Parcel.js para compilação de assets
- **Máscaras**: IMask para CPF, CNPJ, Passaporte (multi-formato), Telefone e CEP
- **Autocomplete**: Sistema AJAX reutilizável para busca de pessoas
- **Paginação Moderna**: Sistema "Carregar mais" com HTMX (20 itens/página)
- **Responsividade**: 
  - Desktop: Sidebar fixa (#333333) + conteúdo principal
  - Mobile: Offcanvas sidebar + botão hamburger
- **Modais**: Sistema HTMX para operações CRUD sem reload
- **⚠️ IMPORTANTE**: Sempre usar componentes Bootstrap (modais, dropdowns, offcanvas, etc.) e HTMX para interações. JavaScript customizado deve ser usado apenas em último caso quando não há solução via Bootstrap/HTMX

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
  - **Sistema de Turismo Completo**:
    - `CiaArea`: Companhias aéreas com código IATA único
    - `Pais`: Países com código ISO de 2 dígitos único
    - `Cidade`: Cidades vinculadas a países
    - `Aeroporto`: Aeroportos com código IATA e timezone
    - `Caravana`: Caravanas com empresa, promotor, líderes e configurações
    - `Incluso`: Itens inclusos/não inclusos nos pacotes
    - `Hotel`: Hotéis com endereço e cidade
    - `Bloqueio`: Bloqueios de passagens com países, hotéis e inclusos
    - `Passageiro`: Passageiros vinculados a bloqueios (Guia, VIP, Free)
    - `Voo`: Voos com companhia, aeroportos e horários
    - `DiaRoteiro`: Roteiro dia-a-dia dos bloqueios
    - `Extra`: Extras opcionais com valores
    - `Tarefa`: Tarefas operacionais (Aéreo, Terrestre, Passageiro)
    - `Nota`: Sistema de notas com threads de resposta
  - **WhatsApp Business**: Contas, templates, mensagens e integração API
- **Configuração**: PostgreSQL (prod) / SQLite (dev)
- **Localização**: PT-BR, timezone America/Sao_Paulo
- **Padrão ForeignKey**: Todos os relacionamentos ForeignKey usam `on_delete=models.PROTECT` por padrão para evitar exclusões acidentais

### 🛠️ Comandos e Ferramentas
- **Seeder**: `python manage.py seed` - Popula dados iniciais (usuário admin, países, whatsapp)
- **Seeder Específico**: `python manage.py seed --seeder paises` - Popula apenas países (193 países)
- **Build**: `npm run build` - Compila assets
- **Testes**: `./test.sh` - Executa 135 testes com InMemoryStorage (sem warnings)
- **Usuário Admin**: 
  - Username: `thiago`
  - Password: `admin123`
  - Grupos: `Administração`, `Comercial`, `Operacional`

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

### 8. Sistema Multi-Área
- [x] **Grupos de Acesso**: Administração, Comercial, Operacional (expansível)
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
- [x] **135 Testes Implementados**: Cobertura completa de todos os models e factories
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
- **3 áreas operacionais**: Administração (gestão) + Comercial (atendimento) + Operacional (turismo)
- **WhatsApp Business completo**: Configuração (admin) + Atendimento (comercial) + **Mídias integradas** + **Janela 24h**
- **Sistema de mídias robusto**: Imagens, vídeos, áudios e documentos com S3 e fallback
- **Sistema de turismo empresarial**: 14 models interconectados para gestão completa
- **Sistema de conversas avançado**: Webhook → Fila → Atribuição → Chat individual → **Verificação 24h** → **Templates automáticos**
- **135 testes implementados**: Sistema de testes robusto com InMemoryStorage
- **UX profissional** com botão scroll, modais inteligentes e layout otimizado
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

### Comandos de Testes
```bash
# Executar todos os 135 testes (recomendado)
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
- **Paginação Moderna**: Sistema "Carregar mais" com HTMX em todas as listagens
- **Busca Otimizada**: Índices Q() para múltiplos campos
- **Asset Bundling**: CSS/JS otimizados via Parcel
- **Cache de Templates**: Rendering otimizado

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

**Última atualização**: 09/12/2025  
**Status**: Sistema empresarial completo com WhatsApp Business integrado, correções no envio de PDFs e sistema de emojis  
**Módulos**: 10+ modelos de dados, sistema completo de mídias, upload de documentos corrigido, interface de chat otimizada

## 🆕 Últimas Atualizações

### 2025 - Melhorias e Funcionalidades Implementadas
- **🌍 Sistema de Países**: 193 países com ISO-2, seeder otimizado via `python manage.py seed --seeder paises`
- **📱 Paginação Moderna**: Sistema "Carregar mais" com HTMX, contador dinâmico de itens restantes
- **🏢 Área Comercial**: Sistema multi-área com grupos, atendimento WhatsApp integrado
- **💬 WhatsApp Business**: 
  - Atendimento completo com fila de conversas e atribuição
  - Sistema de mídias (imagens, vídeos, áudios, documentos) com S3
  - Verificação automática de janela 24h
  - Templates e respostas rápidas

### Dezembro 2025 - Correções e Melhorias WhatsApp
- **📄 PDF Upload Corrigido**: Mensagens PDF agora aparecem corretamente na conversa após envio
  - Criação da mensagem no banco antes do envio via API
  - Status atualizado baseado na resposta da API
  - Função `_send_pdf_whatsapp` refatorada com criação de mensagem
- **😀 Sistema de Emojis**: Seletor dropdown com 38 emojis essenciais para atendimento
  - Inserção inteligente na posição do cursor
  - Interface limpa sem poluir a área de mensagem
  - JavaScript integrado para compatibilidade HTMX
- **⏰ Verificação de Janela 24h**: Bloqueio automático quando fora da janela do WhatsApp
- **🎯 UX Otimizada**: Interface profissional com botão scroll e modais inteligentes