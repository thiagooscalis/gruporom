# Projeto Grupo ROM - Sistema Empresarial Completo

## Resumo do Projeto
Sistema web Django para gerenciamento empresarial com **arquitetura Services + Managers + Properties**, autenticação baseada em grupos, interface Bootstrap 5, sistema completo de vendas de turismo e WhatsApp Business integrado.

## 🏗️ Arquitetura: Services + Managers + Properties

### **Services Layer (Lógica de Negócio)**
```python
# core/services/venda_service.py
class VendaService:
    def criar_venda_bloqueio(dados) -> VendaBloqueio    # Regras de negócio centralizadas
    def adicionar_passageiro_venda(...)                 # Controle de passageiros
    def registrar_pagamento(...)                        # Múltiplos pagamentos
    def confirmar_venda(...)                           # Mudança de status
    def cancelar_venda(...)                            # Cancelamento com motivo
    def listar_vendas_usuario(...)                     # Consultas otimizadas
```

### **Custom Managers (Queries Otimizadas)**
```python
# core/managers/venda_manager.py  
class VendaBloqueioManager:
    def com_totais_calculados()     # Evita N+1 queries
    def ativas()                    # Vendas não canceladas
    def por_status()               # Filtro de status
    def buscar()                   # Busca otimizada
```

### **Properties Inteligentes (Templates)**
```python
# Templates usam properties diretamente
{{ venda.status_display_pt }}      # "Pré-venda", "Confirmada", etc.
{{ venda.valor_formatado }}        # "R$ 1.500,00" 
{{ venda.pode_editar }}            # Regras de negócio
<span class="bg-{{ venda.css_status_class }}">  # Classes Bootstrap
```

## 🔄 Status das Vendas (Simplificado)

### **4 Status Únicos:**
- **🟡 pre-venda** - Vendas em elaboração (pode editar, adicionar passageiros/pagamentos)
- **🟢 confirmada** - Vendas confirmadas (pode adicionar pagamentos, cancelar)
- **🔵 concluída** - Vendas/viagens finalizadas (somente leitura)
- **🔴 cancelada** - Vendas canceladas (somente leitura)

### **Fluxo de Status:**
```
Nova Venda → pre-venda → confirmada → concluída
                ↓
            cancelada (qualquer momento)
```

## ✅ Funcionalidades Implementadas

### 1. **Sistema de Vendas Completo**
- **Pré-vendas**: Listagem focada apenas em vendas `pre-venda`
- **Gerenciar Passageiros**: Modal HTMX com autocomplete de pessoas
- **Registrar Pagamentos**: Múltiplos pagamentos com formas diversas
- **Confirmar/Cancelar**: Modais com validações e motivos
- **Interface Limpa**: Sem coluna status (já filtrada), ações contextuais

### 2. **Sistema de Autenticação**
- Usuário customizado com grupos (Administração, Comercial, Operacional)
- Redirecionamento automático por grupo
- Controle de acesso granular

### 3. **WhatsApp Business Integrado**
- **Configuração**: Contas, templates, API Meta/Facebook
- **Atendimento**: Fila de conversas, atribuição, chat interface
- **Mídias**: Visualização completa de imagens, vídeos, áudios, documentos
- **Janela 24h**: Verificação automática, templates para reativação

### 4. **Sistema de Turismo**
- 14+ models interconectados (Caravanas, Bloqueios, Passageiros, etc.)
- Gestão completa de pacotes turísticos
- Controle de disponibilidade e reservas

### 5. **Interface Profissional**
- Bootstrap 5 customizado (#d3a156)
- Modais HTMX sem JavaScript customizado
- Paginação "Carregar mais"
- Máscaras de entrada inteligentes

## 🛠️ Comandos Essenciais

### Setup
```bash
uv install && npm install && npm run build
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

### Testes
```bash
./test.sh                    # 135+ testes com InMemoryStorage
uv run python manage.py check
```

### Usuário Admin
- **Username**: `thiago`
- **Password**: `admin123`
- **Grupos**: Administração, Comercial, Operacional

## 🗃️ Modelos Principais

### **Gestão de Pessoas**
- `Pessoa`: Dados completos (CPF/CNPJ, endereços)
- `Usuario`: Autenticação customizada
- `Colaborador`: RH completo
- `Fornecedor`: Gestão de fornecedores

### **Sistema de Vendas**
- `VendaBloqueio`: Vendas com properties inteligentes
- `Pagamento`: Múltiplos pagamentos por venda
- `Passageiro`: Passageiros vinculados a vendas
- `ExtraVenda`: Extras opcionais

### **Turismo**
- `Bloqueio`: Pacotes turísticos
- `Caravana`: Grupos organizados
- `Hotel`, `Voo`, `Extra`: Componentes do pacote

## 📱 URLs Principais

### Área Comercial
- `/comercial/pre-vendas/` - Listagem de pré-vendas (apenas status 'pre-venda')
- `/comercial/pre-vendas/{id}/` - Detalhes da venda
- `/comercial/whatsapp/` - Atendimento WhatsApp

### Administração
- `/administracao/` - Dashboard administrativo
- `/administracao/pessoas/` - Gestão de pessoas
- `/administracao/usuarios/` - Gestão de usuários

## 🔧 Configuração Técnica

### **Database**
- PostgreSQL (prod) / SQLite (dev)
- PT-BR, timezone America/Sao_Paulo
- ForeignKey com `on_delete=models.PROTECT` por padrão

### **Frontend**
- Bootstrap 5 + FontAwesome 6
- HTMX para interações dinâmicas
- Parcel.js para build
- Máscaras IMask (CPF, CNPJ, Passaporte, Telefone)

### **Segurança**
- CSRF protection ativo
- LoginRequired middleware
- Controle de acesso baseado em grupos
- Django Admin restrito

---

**Status**: Sistema empresarial completo com arquitetura Services e vendas de turismo  
**Última atualização**: 03/09/2025