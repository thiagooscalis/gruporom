# Campos MultiSelect Globais - Grupo ROM

Sistema unificado de campos de seleção múltipla com interface moderna usando Tom-Select.

## 🎯 Visão Geral

Este sistema fornece campos de formulário padronizados para seleção múltipla (ManyToMany) com:
- Interface moderna e responsiva
- Busca em tempo real
- Tags visuais com remoção
- Suporte a HTMX
- Tema personalizado Grupo ROM

## 📦 Componentes

### 1. Widgets (`core/widgets.py`)
- `MultiSelectWidget` - Widget base para multiselect
- `AutocompleteWidget` - Widget para ForeignKey com busca
- `TagsWidget` - Widget especializado para tags

### 2. Form Fields (`core/form_fields.py`)
- `ModelMultiSelectField` - Campo base para ManyToMany
- `PessoasMultiSelectField` - Especializado para pessoas
- `PaisesMultiSelectField` - Especializado para países
- `EmpresasMultiSelectField` - Especializado para empresas
- `GruposMultiSelectField` - Especializado para grupos de usuário
- `TurnosMultiSelectField` - Especializado para turnos

### 3. Assets
- `tom-select-custom.scss` - Estilos customizados
- `tom-select-init.js` - Inicialização automática

## 🚀 Como Usar

### Uso Básico

```python
from core.form_fields import PaisesMultiSelectField, PessoasMultiSelectField

class MeuForm(forms.ModelForm):
    # Campo de países com interface moderna
    paises = PaisesMultiSelectField(
        queryset=Pais.objects.all(),
        required=True
    )
    
    # Campo de pessoas com busca
    lideres = PessoasMultiSelectField(
        queryset=Pessoa.objects.filter(tipo_doc='CPF'),
        placeholder='Selecione líderes...',
        max_options=5
    )
```

### Uso Avançado

```python
from core.form_fields import ModelMultiSelectField
from core.widgets import MultiSelectWidget

class FormAvancado(forms.ModelForm):
    # Campo customizado com todas as opções
    items = ModelMultiSelectField(
        queryset=MinhaModel.objects.all(),
        widget=MultiSelectWidget(
            placeholder='Selecione itens...',
            search_placeholder='Digite para buscar...',
            no_results_text='Nada encontrado',
            max_options=10,
            create=True,  # Permite criar novos itens
            create_text='Criar novo: ',
            remove_button=True,
            clear_button=True
        )
    )
```

### Funções de Conveniência

```python
from core.form_fields import (
    create_pessoas_field, 
    create_paises_field, 
    create_empresas_field
)

class FormRapido(forms.Form):
    # Criação rápida de campos
    colaboradores = create_pessoas_field(
        queryset=Pessoa.objects.filter(ativo=True),
        placeholder='Selecione colaboradores...'
    )
    
    destinos = create_paises_field(
        placeholder='Países de destino...'
    )
    
    empresas = create_empresas_field(
        tipo_empresa='Turismo',
        placeholder='Empresas de turismo...'
    )
```

## 🎨 Personalização de Aparência

### CSS Customizado
```css
/* Personalizar cores */
.tom-select-bootstrap .ts-item {
    background: #d3a156; /* Cor primária do Grupo ROM */
    color: #fff;
}

.tom-select-bootstrap .ts-wrapper.focus {
    border-color: #d3a156;
    box-shadow: 0 0 0 0.25rem rgba(211, 161, 86, 0.25);
}
```

### Template HTML
```html
<!-- Incluir CSS e JS -->
{% block extra_css %}
<link href="https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/css/tom-select.bootstrap5.css" rel="stylesheet">
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/js/tom-select.complete.min.js"></script>
<script>
// Inicialização automática funciona com HTMX
document.addEventListener('htmx:afterSwap', function(e) {
    initTomSelectFields(e.detail.target);
});
</script>
{% endblock %}

<!-- Campo no template -->
<div class="mb-3">
    <label for="paises" class="form-label">Países</label>
    <select class="form-select tom-select-field" name="paises" multiple
            data-placeholder="Selecione países..."
            data-search-placeholder="Digite para buscar..."
            data-no-results-text="Nenhum país encontrado">
        {% for pais in paises %}
        <option value="{{ pais.id }}">{{ pais.nome }}</option>
        {% endfor %}
    </select>
</div>
```

## 🔧 Opções Disponíveis

### Parâmetros do Widget
- `placeholder` - Texto quando vazio
- `search_placeholder` - Texto da busca
- `no_results_text` - Mensagem sem resultados
- `max_options` - Limite de seleções
- `create` - Permitir criar novos itens
- `create_text` - Texto para criação
- `remove_button` - Botão de remover tags
- `clear_button` - Botão de limpar tudo

### Data Attributes
```html
<select class="tom-select-field" 
        data-placeholder="Selecione..."
        data-max-options="5"
        data-create="true"
        data-remove-button="true"
        data-clear-button="true">
```

## 🔌 Integração com HTMX

### Inicialização Automática
O sistema detecta automaticamente:
- Carregamento inicial da página
- Atualizações via HTMX (`htmx:afterSwap`)
- Abertura de modais Bootstrap
- Limpeza ao fechar modais

### Eventos Customizados
```javascript
// Escutar eventos do Tom-Select
document.addEventListener('tomselect:add', function(e) {
    console.log('Item adicionado:', e.detail.value);
});

document.addEventListener('tomselect:remove', function(e) {
    console.log('Item removido:', e.detail.value);
});
```

## 📋 Campos Especializados Disponíveis

### PessoasMultiSelectField
```python
# Para líderes, colaboradores, etc.
lideres = PessoasMultiSelectField(
    queryset=Pessoa.objects.filter(tipo_doc='CPF'),
    placeholder='Selecione pessoas...'
)
# Exibe: "João Silva - 123.456.789-00"
```

### PaisesMultiSelectField
```python
# Para destinos, roteiros, etc.
destinos = PaisesMultiSelectField(
    queryset=Pais.objects.all(),
    placeholder='Selecione países...'
)
# Exibe: "Brasil (BR)"
```

### EmpresasMultiSelectField
```python
# Para empresas parceiras, fornecedores, etc.
fornecedores = EmpresasMultiSelectField(
    queryset=Pessoa.objects.filter(tipo_empresa='Turismo'),
    placeholder='Selecione empresas...'
)
# Exibe: "ROM Turismo - 12.345.678/0001-90"
```

### GruposMultiSelectField
```python
# Para grupos de usuário
grupos = GruposMultiSelectField(
    queryset=Group.objects.all(),
    max_options=5,
    placeholder='Selecione grupos...'
)
```

### TurnosMultiSelectField
```python
# Para turnos de trabalho
turnos = TurnosMultiSelectField(
    queryset=Turno.objects.all(),
    placeholder='Selecione turnos...'
)
# Exibe: "Manhã - 08:00 às 17:00"
```

## 🏗️ Exemplos Práticos

### Formulário de Caravana
```python
from core.form_fields import PaisesMultiSelectField, PessoasMultiSelectField

class CaravanaForm(forms.ModelForm):
    paises = PaisesMultiSelectField(
        queryset=Pais.objects.all().order_by('nome'),
        label='Países do Roteiro',
        required=True
    )
    
    lideres = PessoasMultiSelectField(
        queryset=Pessoa.objects.filter(tipo_doc='CPF').order_by('nome'),
        label='Líderes da Caravana',
        required=False,
        max_options=3
    )
    
    class Meta:
        model = Caravana
        fields = ['nome', 'paises', 'lideres', ...]
```

### Formulário de Usuário
```python
from core.form_fields import GruposMultiSelectField, EmpresasMultiSelectField

class UsuarioForm(forms.ModelForm):
    groups = GruposMultiSelectField(
        queryset=Group.objects.all(),
        label='Grupos de Acesso',
        max_options=5
    )
    
    empresas = EmpresasMultiSelectField(
        queryset=Pessoa.objects.filter(empresa_gruporom=True),
        label='Empresas Associadas'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'groups', 'empresas', ...]
```

## 📱 Responsividade

O sistema é totalmente responsivo:
- **Desktop**: Dropdown completo com busca
- **Mobile**: Interface adaptada para toque
- **Modais**: Z-index ajustado automaticamente

## ⚡ Performance

- **Lazy Loading**: Inicialização apenas quando necessário
- **Event Delegation**: Eventos eficientes
- **Memory Management**: Limpeza automática em modais
- **CDN**: Assets carregados via CDN para velocidade

## 🐛 Troubleshooting

### Tom-Select não aparece
1. Verifique se o CSS/JS está carregado
2. Confirme a classe `tom-select-field`
3. Verifique o console por erros

### HTMX não reinicializa
1. Confirme o event listener `htmx:afterSwap`
2. Verifique se o container tem a classe correta
3. Use `initTomSelectFields()` manualmente se necessário

### Estilos não aplicados
1. Confirme a classe `tom-select-bootstrap`
2. Verifique conflitos de CSS
3. Ajuste z-index se em modais

## 🔮 Roadmap

- [ ] Suporte a Select2 como alternativa
- [ ] Lazy loading para grandes datasets
- [ ] Integração com API externa
- [ ] Temas adicionais
- [ ] Modo dark automático
- [ ] Cache de opções

---

**Documentação criada em**: Agosto 2025  
**Versão**: 1.0  
**Compatibilidade**: Django 4.2+, Bootstrap 5, Tom-Select 2.3+