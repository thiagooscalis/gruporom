# Padrão de Paginação "Carregar Mais" - Guia de Implementação

## Overview
Este documento descreve como implementar o padrão "Carregar Mais" com HTMX em novas listagens.

## 1. Estrutura de Arquivos

Para cada listagem, criar 3 templates:

```
app/templates/administracao/modelo/
├── lista.html              # Template principal com busca
├── partial_lista.html       # Tabela completa + botão carregar mais  
└── partial_linhas.html      # Apenas <tr> para append incremental
```

## 2. View Pattern

```python
from django.core.paginator import Paginator

def lista(request):
    # Filtros e busca
    search = request.GET.get('search', '')
    
    # Query base
    objetos = Modelo.objects.all()
    
    # Aplicar filtros
    if search:
        objetos = objetos.filter(nome__icontains=search)
    
    # Paginação (SEMPRE 20 itens)
    paginator = Paginator(objetos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'restantes': page_obj.paginator.count - page_obj.end_index() if page_obj else 0,
    }
    
    # HTMX Detection
    if request.headers.get('HX-Request'):
        if request.GET.get('load_more'):
            return render(request, 'app/partial_linhas.html', context)  # Append
        else:
            return render(request, 'app/partial_lista.html', context)   # Replace
    
    return render(request, 'app/lista.html', context)
```

## 3. Template Principal (lista.html)

```html
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <!-- Breadcrumbs -->
            {% include 'includes/breadcrumbs.html' with prev_page='Administração' prev_url='/administracao/' cur_page='Objetos' %}
            
            <!-- Busca e Filtros -->
            <div class="card mb-4">
                <div class="card-body">
                    <form method="get" class="row g-3" 
                          hx-get="{% url 'app:lista' %}"
                          hx-target="#objetos-lista"
                          hx-swap="outerHTML"
                          hx-push-url="true"
                          hx-trigger="submit">
                        <div class="col-md-10">
                            <input type="text" name="search" class="form-control" 
                                   placeholder="Buscar..." 
                                   value="{{ search }}">
                        </div>
                        <div class="col-md-2">
                            <button type="submit" class="btn btn-secondary w-100">
                                <i class="fas fa-search me-2"></i>Buscar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- Listagem (via partial com HTMX) -->
            {% include 'app/partial_lista.html' %}
        </div>
    </div>
</div>

<!-- Floating Action Button -->
<a href="#" class="btn btn-primary rounded-circle fixed-br d-flex align-items-center justify-content-center"
   style="width: 56px; height: 56px;"
   hx-get="{% url 'app:novo_modal' %}"
   hx-target="body"
   hx-swap="beforeend"
   title="Novo Objeto">
    <i class="fas fa-plus text-white"></i>
</a>
{% endblock %}
```

## 4. Template Partial Completo (partial_lista.html)

```html
{% load core_tags %}

<!-- Listagem -->
<div class="card" id="objetos-lista">
    <div class="card-body">
        {% if page_obj %}
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Campo 1</th>
                        <th>Campo 2</th>
                        <th width="120">Ações</th>
                    </tr>
                </thead>
                <tbody id="objetos-tbody">
                    {% for objeto in page_obj %}
                    <tr>
                        <td>{{ objeto.campo1 }}</td>
                        <td>{{ objeto.campo2 }}</td>
                        <td>
                            <button type="button" class="btn btn-sm btn-outline-primary" title="Editar"
                                    hx-get="{% url 'app:editar_modal' objeto.pk %}"
                                    hx-target="body"
                                    hx-swap="beforeend">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger" title="Excluir"
                                    hx-get="{% url 'app:excluir_modal' objeto.pk %}"
                                    hx-target="body"
                                    hx-swap="beforeend">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="3" class="text-center text-muted py-4">
                            Nenhum objeto encontrado
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- Botão Carregar Mais -->
        {% if page_obj.has_next %}
        <div class="text-center mt-4" id="carregar-mais-container">
            <button type="button" class="btn btn-outline-primary"
                    hx-get="{% url 'app:lista' %}?page={{ page_obj.next_page_number }}{% if search %}&search={{ search }}{% endif %}&load_more=1"
                    hx-target="#objetos-tbody"
                    hx-swap="beforeend">
                <i class="fas fa-plus me-2"></i>Carregar mais ({{ restantes }} restantes)
            </button>
        </div>
        {% endif %}
        {% else %}
        <p class="text-center text-muted">Nenhum objeto cadastrado.</p>
        {% endif %}
    </div>
</div>
```

## 5. Template Linhas Incrementais (partial_linhas.html)

```html
{% load core_tags %}

<!-- Linhas adicionais para "Carregar mais" -->
{% for objeto in page_obj %}
<tr>
    <td>{{ objeto.campo1 }}</td>
    <td>{{ objeto.campo2 }}</td>
    <td>
        <button type="button" class="btn btn-sm btn-outline-primary" title="Editar"
                hx-get="{% url 'app:editar_modal' objeto.pk %}"
                hx-target="body"
                hx-swap="beforeend">
            <i class="fas fa-edit"></i>
        </button>
        <button type="button" class="btn btn-sm btn-outline-danger" title="Excluir"
                hx-get="{% url 'app:excluir_modal' objeto.pk %}"
                hx-target="body"
                hx-swap="beforeend">
            <i class="fas fa-trash"></i>
        </button>
    </td>
</tr>
{% endfor %}

<!-- Atualizar botão Carregar Mais -->
{% if page_obj.has_next %}
<script>
// Atualizar o botão existente
document.querySelector('#carregar-mais-container button').setAttribute('hx-get', 
    '{% url "app:lista" %}?page={{ page_obj.next_page_number }}{% if search %}&search={{ search }}{% endif %}&load_more=1'
);
document.querySelector('#carregar-mais-container button').innerHTML = 
    '<i class="fas fa-plus me-2"></i>Carregar mais ({{ restantes }} restantes)';
// Re-processar HTMX
htmx.process(document.querySelector('#carregar-mais-container'));
</script>
{% else %}
<script>
// Remover botão se não há mais páginas
document.querySelector('#carregar-mais-container').remove();
</script>
{% endif %}
```

## 6. Testes Recomendados

```python
def test_botao_carregar_mais_aparece(self):
    """Testa se o botão aparece quando há mais páginas"""
    # Criar mais de 20 objetos
    for i in range(25):
        ObjetoFactory()
    
    response = self.client.get(reverse('app:lista'))
    self.assertContains(response, 'Carregar mais')

def test_carregar_mais_htmx_append(self):
    """Testa se HTMX retorna apenas linhas para append"""
    response = self.client.get(
        reverse('app:lista') + '?page=2&load_more=1',
        HTTP_HX_REQUEST='true'
    )
    self.assertTemplateUsed(response, 'app/partial_linhas.html')
```

## 7. Checklist de Implementação

- [ ] View com detection HTMX (`HX-Request` header)
- [ ] Context com `restantes` calculado
- [ ] Template principal com formulário HTMX
- [ ] Template partial com `tbody id="objetos-tbody"`
- [ ] Template linhas com script de atualização do botão
- [ ] Botão carregar mais com target `#objetos-tbody`
- [ ] Filtros preservados nos links HTMX
- [ ] Testes de funcionalidade básica
- [ ] Paginação de 20 itens/página

## 8. Vantagens da Implementação

- ✅ **UX Moderna**: Scroll infinito mais intuitivo
- ✅ **Performance**: Apenas linhas adicionais carregadas
- ✅ **Mobile Friendly**: Melhor em dispositivos móveis
- ✅ **URL Preservada**: Bookmarks funcionam
- ✅ **Filtros Mantidos**: Busca preservada na paginação
- ✅ **Contador Visual**: Usuário sabe quantos restam