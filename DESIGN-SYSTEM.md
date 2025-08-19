# 🎨 Design System - Grupo ROM

## Visão Geral

Sistema de design baseado nas cores oficiais do logo Grupo ROM, utilizando cinza chumbo como cor neutra principal, construído com Tailwind CSS para garantir consistência visual e facilidade de manutenção.

## 🌈 Paleta de Cores

### Cores Primárias (Logo Grupo ROM)
Baseadas no gradiente oficial do logo:

```css
primary-50:  #fdfcf7  /* Muito claro - backgrounds sutis */
primary-100: #faf6eb  /* Claro - hover states */
primary-200: #f4ebd2  /* Cards, containers */
primary-300: #ecdab3  /* Borders, dividers */
primary-400: #e0c785  /* Disabled states */
primary-500: #d3a156  /* ★ Principal - cor do logo */
primary-600: #c8944a  /* Hover - botões primários */
primary-700: #b5803c  /* Active - botões primários */
primary-800: #965915  /* ★ Escuro - do gradiente logo */
primary-900: #7a4811  /* Muito escuro - textos */
primary-950: #4a2b0a  /* Ultra escuro */
```

### Cinza Chumbo (Neutros)
Paleta principal para textos e backgrounds:

```css
slate-50:  #f8fafc  /* Muito claro */
slate-100: #f1f5f9  /* Claro */
slate-200: #e2e8f0  /* Borders sutis */
slate-300: #cbd5e1  /* Borders, placeholders */
slate-400: #94a3b8  /* Text muted */
slate-500: #64748b  /* Text secondary */
slate-600: #475569  /* Text primary */
slate-700: #334155  /* ★ Sidebar - cinza chumbo */
slate-800: #1e293b  /* Escuro */
slate-900: #0f172a  /* Ultra escuro */
slate-950: #020617  /* Black alternative */
```

### Estados Semânticos

**Sucesso (Verde)**
```css
success-50:  #f0fdf4
success-100: #dcfce7
success-500: #22c55e  /* ★ Padrão */
success-600: #16a34a  /* Hover */
success-700: #15803d  /* Active */
```

**Aviso (Amarelo)**
```css
warning-50:  #fffbeb
warning-100: #fef3c7
warning-500: #f59e0b  /* ★ Padrão */
warning-600: #d97706  /* Hover */
warning-700: #b45309  /* Active */
```

**Erro (Vermelho)**
```css
danger-50:  #fef2f2
danger-100: #fee2e2
danger-500: #ef4444  /* ★ Padrão */
danger-600: #dc2626  /* Hover */
danger-700: #b91c1c  /* Active */
```

**Informação (Azul)**
```css
info-50:  #eff6ff
info-100: #dbeafe
info-500: #3b82f6  /* ★ Padrão */
info-600: #2563eb  /* Hover */
info-700: #1d4ed8  /* Active */
```

## 🖱️ Componentes

### Botões

**Primário (Dourado)**
```html
<button class="btn-primary">Salvar</button>
<!-- ou -->
<button class="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-md">
  Salvar
</button>
```

**Secundário (Cinza)**
```html
<button class="btn-secondary">Cancelar</button>
```

**Estados**
```html
<button class="btn-success">Confirmar</button>
<button class="btn-danger">Excluir</button>
```

### Cards

```html
<div class="card">
  <div class="card-header">
    <h3 class="text-lg font-semibold text-slate-900">Título</h3>
  </div>
  <div class="card-body">
    <p class="text-slate-600">Conteúdo do card...</p>
  </div>
  <div class="card-footer">
    <button class="btn-primary">Ação</button>
  </div>
</div>
```

### Badges/Tags

```html
<span class="badge-primary">Ativo</span>
<span class="badge-success">Aprovado</span>
<span class="badge-warning">Pendente</span>
<span class="badge-danger">Rejeitado</span>
<span class="badge-slate">Neutro</span>
```

### Formulários

```html
<input type="text" class="form-input" placeholder="Digite aqui...">
<select class="form-select">
  <option>Selecione...</option>
</select>
<textarea class="form-textarea" rows="4"></textarea>
```

### Alertas

```html
<div class="alert-success">
  <p>Operação realizada com sucesso!</p>
</div>
<div class="alert-warning">
  <p>Atenção: Verifique os dados antes de continuar.</p>
</div>
<div class="alert-danger">
  <p>Erro: Não foi possível completar a operação.</p>
</div>
<div class="alert-info">
  <p>Informação: Novos recursos disponíveis.</p>
</div>
```

### Sidebar (Cinza Chumbo)

```html
<nav class="sidebar">
  <a href="#" class="sidebar-item active">
    <svg class="w-5 h-5 mr-3">...</svg>
    Dashboard
  </a>
  <a href="#" class="sidebar-item">
    <svg class="w-5 h-5 mr-3">...</svg>
    Usuários
  </a>
</nav>
```

### Tabelas

```html
<table class="table">
  <thead>
    <tr>
      <th>Nome</th>
      <th>Email</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>João Silva</td>
      <td>joao@exemplo.com</td>
      <td><span class="badge-success">Ativo</span></td>
    </tr>
  </tbody>
</table>
```

## ✍️ Tipografia

### Tamanhos
```css
text-xs:   0.75rem (12px)
text-sm:   0.875rem (14px)
text-base: 1rem (16px)      ★ Padrão
text-lg:   1.125rem (18px)
text-xl:   1.25rem (20px)
text-2xl:  1.5rem (24px)
text-3xl:  1.875rem (30px)
```

### Pesos
```css
font-normal:    400  ★ Texto comum
font-medium:    500  ★ Subtítulos
font-semibold:  600  ★ Títulos
font-bold:      700  ★ Destaques
```

### Cores de Texto
```css
text-slate-900: #0f172a  ★ Títulos principais
text-slate-700: #334155  ★ Texto primário
text-slate-500: #64748b  ★ Texto secundário
text-slate-400: #94a3b8  ★ Placeholders, texto muted
text-primary-600: #c8944a  ★ Links, destaques dourados
```

## 📐 Espaçamentos

### Sistema de Grid (8px base)
```css
space-1:  0.25rem (4px)
space-2:  0.5rem (8px)
space-3:  0.75rem (12px)
space-4:  1rem (16px)      ★ Padrão interno
space-6:  1.5rem (24px)    ★ Seções
space-8:  2rem (32px)      ★ Containers
space-12: 3rem (48px)      ★ Layouts
```

### Customizados
```css
space-18: 4.5rem (72px)
space-22: 5.5rem (88px)
space-26: 6.5rem (104px)
space-30: 7.5rem (120px)
```

## 🔘 Bordas e Sombras

### Raios de Borda
```css
rounded-sm:  0.125rem (2px)
rounded:     0.25rem (4px)   ★ Padrão
rounded-md:  0.375rem (6px)  ★ Cards, botões
rounded-lg:  0.5rem (8px)    ★ Modais
rounded-xl:  0.75rem (12px)
rounded-2xl: 1rem (16px)
```

### Sombras
```css
shadow-sm:      Sutil
shadow:         Padrão
shadow-md:      Cards
shadow-lg:      Modais
shadow-primary: Sombra dourada (primary)
```

## 🎯 Padrões de Uso

### Hierarquia Visual
1. **H1**: `text-3xl font-bold text-slate-900` - Títulos principais
2. **H2**: `text-2xl font-semibold text-slate-800` - Seções
3. **H3**: `text-lg font-medium text-slate-700` - Subsections
4. **Body**: `text-base text-slate-600` - Texto comum
5. **Small**: `text-sm text-slate-500` - Texto auxiliar

### Estados Interativos
```css
/* Hover */
hover:bg-primary-600
hover:text-primary-700
hover:border-primary-500

/* Focus */
focus:ring-2
focus:ring-primary-500
focus:border-transparent

/* Active */
active:bg-primary-700
active:transform
active:scale-95
```

### Combinações Recomendadas

**Card Principal**
```html
<div class="bg-white rounded-lg shadow-md border border-slate-200 p-6">
```

**Botão Destaque**
```html
<button class="bg-primary-500 hover:bg-primary-600 text-white font-medium px-6 py-3 rounded-md shadow-primary transition-all">
```

**Input com Label**
```html
<label class="block text-sm font-medium text-slate-700 mb-2">
<input class="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent">
```

## 🎨 Classes Utilitárias Especiais

### Gradiente do Logo
```css
.bg-gradient-rom
/* Usa o gradiente exato do logo: #965915 → #ddb14b → #f9e7a1 */
```

### Texto com Cor da Marca
```css
.text-grupo-rom  /* Equivale a text-primary-600 */
```

### Responsividade
```css
.mobile-only    /* Visível apenas no mobile */
.desktop-only   /* Visível apenas no desktop */
```

### Print
```css
.no-print      /* Oculta na impressão */
.print-only    /* Visível apenas na impressão */
```

## 📱 Breakpoints Responsivos

```css
sm:   640px   /* Tablets pequenos */
md:   768px   /* ★ Tablets */
lg:   1024px  /* ★ Desktops */
xl:   1280px  /* Desktops grandes */
2xl:  1536px  /* Ultra wide */
```

## ⚡ Performance e Boas Práticas

### Classes Recomendadas para Performance
1. Use classes utilitárias ao invés de CSS customizado
2. Prefira `bg-primary-500` ao invés de `style="background: #d3a156"`
3. Combine classes relacionadas: `px-4 py-2` → `p-4`
4. Use breakpoints responsivos conscientemente

### Acessibilidade
- Contraste mínimo 4.5:1 para texto normal
- Contraste mínimo 3:1 para texto grande
- Focus visível em elementos interativos
- Cores não são a única forma de transmitir informação

---

**Versão**: 1.0.0  
**Última atualização**: Agosto 2025  
**Baseado em**: Logo oficial Grupo ROM + Tailwind CSS 3.4