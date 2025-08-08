from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models import Pessoa, Funcao
from core.choices import TIPO_DOC_CHOICES, SEXO_CHOICES


@login_required
def redirect_to_group(request):
    """
    View que redireciona para o primeiro grupo encontrado no usuário.
    Se o usuário não tiver grupos, faz logout e exibe mensagem de erro.
    """
    user = request.user

    # Verifica se o usuário tem grupos
    user_groups = user.groups.all()

    if not user_groups.exists():
        # Faz logout e exibe mensagem
        logout(request)
        messages.error(
            request, "O usuário deve ter uma área de acesso"
        )
        return redirect("/login/")

    # Redireciona para o primeiro grupo
    first_group = user_groups.first()
    group_name = slugify(first_group.name)
    
    # Redireciona baseado no nome do grupo
    return redirect(f"/{group_name}/")


def privacidade_inclusive(request):
    """
    View pública para exibir a política de privacidade da Inclusive Travel.
    """
    return render(request, 'inclusive/privacidade.html')


def termos_inclusive(request):
    """
    View pública para exibir os termos de serviço da Inclusive Travel.
    """
    return render(request, 'inclusive/termos.html')


def pode_cadastrar_pessoa(user):
    """
    Verifica se o usuário pode cadastrar pessoas.
    Usuários dos grupos Administração, Comercial e Operacional podem cadastrar.
    """
    grupos_permitidos = ['Administração', 'Comercial', 'Operacional']
    return user.groups.filter(name__in=grupos_permitidos).exists()


@login_required
@require_http_methods(["GET", "POST"])
def cadastrar_pessoa_view(request):
    """
    View para cadastro de pessoa via HTMX modal.
    Acessível por usuários de qualquer área com permissão para cadastrar.
    """
    # Verificar permissões
    if not pode_cadastrar_pessoa(request.user):
        return JsonResponse({
            'error': 'Você não tem permissão para cadastrar pessoas'
        }, status=403)
    
    if request.method == 'GET':
        # Retorna o modal vazio para cadastro
        context = {
            'tipos_doc': TIPO_DOC_CHOICES,
            'sexo_choices': SEXO_CHOICES,
            'funcoes': Funcao.objects.all().order_by('masculino')
        }
        return render(request, 'pessoa/modal_cadastrar.html', context)
    
    elif request.method == 'POST':
        try:
            # Extrair dados do formulário
            nome = request.POST.get('nome', '').strip()
            doc = request.POST.get('doc', '').strip()
            tipo_doc = request.POST.get('tipo_doc', '').strip()
            celular = request.POST.get('celular', '').strip()
            email = request.POST.get('email', '').strip()
            sexo = request.POST.get('sexo', '').strip() or None
            funcao_id = request.POST.get('funcao', '').strip() or None
            
            # Validações básicas
            errors = []
            
            if not nome:
                errors.append('Nome é obrigatório')
            
            if not doc:
                errors.append('Documento é obrigatório')
            elif Pessoa.objects.filter(doc=doc).exists():
                errors.append('Já existe uma pessoa cadastrada com este documento')
            
            if not tipo_doc or tipo_doc not in [choice[0] for choice in TIPO_DOC_CHOICES]:
                errors.append('Tipo de documento inválido')
            
            if not celular:
                errors.append('Celular é obrigatório')
            
            if not email:
                errors.append('E-mail é obrigatório')
            elif Pessoa.objects.filter(email=email).exists():
                errors.append('Já existe uma pessoa cadastrada com este e-mail')
            
            # Validar função se fornecida
            funcao_obj = None
            if funcao_id:
                try:
                    funcao_obj = Funcao.objects.get(id=funcao_id)
                except Funcao.DoesNotExist:
                    errors.append('Função selecionada não existe')
            
            # Validar sexo se fornecido
            if sexo and sexo not in [choice[0] for choice in SEXO_CHOICES]:
                errors.append('Sexo selecionado inválido')
            
            if errors:
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
            
            # Criar pessoa
            pessoa = Pessoa.objects.create(
                nome=nome,
                doc=doc,
                tipo_doc=tipo_doc,
                celular=celular,
                email=email,
                sexo=sexo,
                funcao=funcao_obj
            )
            
            # Preparar nome de exibição com título se existir
            display_name_parts = []
            if pessoa.funcao and pessoa.sexo:
                titulo = pessoa.funcao.get_abreviacao_por_sexo(pessoa.sexo)
                display_name_parts.append(f"{titulo} {pessoa.nome}")
            else:
                display_name_parts.append(pessoa.nome)
            
            if pessoa.doc:
                display_name_parts.append(pessoa.doc)
            if pessoa.celular:
                display_name_parts.append(pessoa.celular)
            
            display_name = " - ".join(display_name_parts)
            
            return JsonResponse({
                'success': True,
                'message': f'Pessoa "{str(pessoa)}" cadastrada com sucesso!',
                'pessoa': {
                    'id': pessoa.id,
                    'nome': pessoa.nome,
                    'doc': pessoa.doc,
                    'celular': pessoa.celular,
                    'display_name': display_name
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao cadastrar pessoa: {str(e)}'
            }, status=500)
