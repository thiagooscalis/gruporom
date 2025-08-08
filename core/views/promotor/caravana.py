# -*- coding: utf-8 -*-
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from core.models import Caravana, Pessoa, Bloqueio, Pais, Aeroporto
from core.forms.caravana_promotor import CaravanaPromotorForm


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Promotor').exists())
def cadastrar_caravana_view(request):
    """
    View principal para cadastrar caravana com HTMX multistep
    """
    # Inicializar sessão se necessário
    init_session(request)
    
    # Se for requisição HTMX
    if request.headers.get('HX-Request'):
        return handle_htmx_request(request)
    
    # Primeira renderização da página - limpar sessão
    clear_session(request)
    
    context = {
        'title': 'Cadastrar Caravana',
    }
    
    return render(request, 'promotor/cadastrar_caravana.html', context)


def init_session(request):
    """Inicializa a sessão se necessário"""
    if 'caravana_data' not in request.session:
        request.session['caravana_data'] = {}
        request.session['lideres_data'] = []
        request.session['current_step'] = 1


def clear_session(request):
    """Limpa os dados da sessão"""
    request.session['caravana_data'] = {}
    request.session['lideres_data'] = []
    request.session['current_step'] = 1


def handle_htmx_request(request):
    """Processa requisições HTMX"""
    if request.method == 'POST':
        step = int(request.POST.get('current_step', 1))
        save_step_data(request, step)
        
        action = request.POST.get('action')
        
        if action == 'next':
            request.session['current_step'] = min(step + 1, 4)
        elif action == 'previous':
            request.session['current_step'] = max(step - 1, 1)
        elif action == 'submit':
            return process_submission(request)
        elif action == 'add_lider':
            return add_lider(request)
        elif action == 'remove_lider':
            return remove_lider(request)
    
    step = request.session.get('current_step', 1)
    return render_step(request, step)


def save_step_data(request, step):
    """Salva os dados do step atual na sessão"""
    data = request.session.get('caravana_data', {})
    
    step_handlers = {
        1: save_step1_data,
        3: save_step3_data,
        4: save_step4_data,
    }
    
    handler = step_handlers.get(step)
    if handler:
        handler(request, data)
    
    request.session['caravana_data'] = data
    request.session.modified = True


def save_step1_data(request, data):
    """Salva dados do Step 1 - Dados da Caravana"""
    data['nome'] = request.POST.get('nome', '')
    data['data_saida'] = request.POST.get('data_saida', '')
    data['empresa'] = request.POST.get('empresa', '')
    data['tipo'] = request.POST.get('tipo', '')
    data['paises'] = request.POST.getlist('paises')
    data['aeroporto_embarque'] = request.POST.get('aeroporto_embarque', '')


def save_step3_data(request, data):
    """Salva dados do Step 3 - Responsável"""
    data['responsavel_doc'] = request.POST.get('responsavel_doc', '')
    data['responsavel_nome'] = request.POST.get('responsavel_nome', '')
    data['responsavel_celular'] = request.POST.get('responsavel_celular', '')
    data['responsavel_email'] = request.POST.get('responsavel_email', '')


def save_step4_data(request, data):
    """Salva dados do Step 4 - Valores e Configurações"""
    data['valor'] = request.POST.get('valor', '')
    data['moeda'] = request.POST.get('moeda', '')
    data['taxas'] = request.POST.get('taxas', '')
    data['moeda_taxas'] = request.POST.get('moeda_taxas', '')
    data['data_contrato'] = request.POST.get('data_contrato', '')
    data['quantidade'] = request.POST.get('quantidade', '')
    data['free_economica'] = request.POST.get('free_economica', '0')
    data['free_executiva'] = request.POST.get('free_executiva', '0')
    data['repasse_valor'] = request.POST.get('repasse_valor', '')
    data['repasse_tipo'] = request.POST.get('repasse_tipo', '')
    data['link'] = request.POST.get('link', '')


def render_step(request, step):
    """Renderiza o step específico"""
    template_map = {
        1: 'promotor/partials/caravana_step1.html',
        2: 'promotor/partials/caravana_step2.html',
        3: 'promotor/partials/caravana_step3.html',
        4: 'promotor/partials/caravana_step4.html',
    }
    
    context = get_step_context(request, step)
    return render(request, template_map[step], context)


def get_step_context(request, step):
    """Retorna o contexto para o step específico"""
    context = {
        'current_step': step,
        'data': request.session.get('caravana_data', {}),
        'lideres': request.session.get('lideres_data', []),
    }
    
    if step == 1:
        context.update({
            'empresas': Pessoa.objects.filter(empresa_gruporom=True, tipo_empresa='Turismo').order_by('nome'),
            'paises': Pais.objects.all().order_by('nome'),
            'aeroportos': Aeroporto.objects.select_related('cidade__pais').order_by('nome'),
            'tipos': [
                ('Evangélica', 'Evangélica'),
                ('Católica', 'Católica'),
                ('Lazer', 'Lazer'),
                ('Mentoria', 'Mentoria'),
            ]
        })
    elif step == 2:
        context.update({
            'pessoas': Pessoa.objects.filter(tipo_doc='CPF').order_by('nome')
        })
    elif step == 4:
        context.update({
            'moedas': [
                ('Real', 'Real (BRL)'),
                ('Dólar', 'Dólar (USD)'),
                ('Euro', 'Euro (EUR)'),
            ],
            'repasse_tipos': [
                ('Total', 'Total'),
                ('Por Passageiro', 'Por Passageiro'),
            ]
        })
    
    return context


def add_lider(request):
    """Adiciona um líder via HTMX"""
    lideres = request.session.get('lideres_data', [])
    
    novo_lider = {
        'doc': request.POST.get('lider_doc', ''),
        'nome': request.POST.get('lider_nome', ''),
        'celular': request.POST.get('lider_celular', ''),
        'email': request.POST.get('lider_email', ''),
    }
    
    if novo_lider['doc'] and novo_lider['nome']:
        lideres.append(novo_lider)
        request.session['lideres_data'] = lideres
        request.session.modified = True
    
    context = {
        'lideres': lideres,
        'current_step': 2,
    }
    
    return render(request, 'promotor/partials/lideres_list.html', context)


def remove_lider(request):
    """Remove um líder via HTMX"""
    lideres = request.session.get('lideres_data', [])
    index = int(request.POST.get('lider_index', -1))
    
    if 0 <= index < len(lideres):
        lideres.pop(index)
        request.session['lideres_data'] = lideres
        request.session.modified = True
    
    context = {
        'lideres': lideres,
        'current_step': 2,
    }
    
    return render(request, 'promotor/partials/lideres_list.html', context)


def process_submission(request):
    """Processa o envio final do formulário"""
    data = request.session.get('caravana_data', {})
    lideres_data = request.session.get('lideres_data', [])
    
    try:
        with transaction.atomic():
            # Criar responsável
            responsavel = create_or_update_pessoa(
                doc=data.get('responsavel_doc', ''),
                nome=data.get('responsavel_nome', ''),
                telefone=data.get('responsavel_celular', ''),
                email=data.get('responsavel_email', '')
            )
            
            # Obter ou criar promotor
            promotor = get_or_create_promotor(request.user)
            
            # Criar caravana
            caravana = create_caravana(data, promotor, responsavel)
            
            # Processar líderes
            process_lideres(caravana, lideres_data)
            
            # Criar bloqueio inicial
            create_initial_bloqueio(caravana, data)
            
            # Limpar sessão
            clear_session(request)
            
            messages.success(request, f'Caravana "{caravana.nome}" cadastrada com sucesso!')
            
            # Retornar resposta HTMX com redirect
            response = HttpResponse()
            response['HX-Redirect'] = '/promotor/'
            return response
            
    except Exception as e:
        messages.error(request, f'Erro ao cadastrar caravana: {str(e)}')
        return render_step(request, 4)


def create_or_update_pessoa(doc, nome, telefone, email):
    """Cria ou atualiza uma pessoa"""
    doc_limpo = doc.replace('.', '').replace('-', '').replace('/', '')
    
    pessoa, created = Pessoa.objects.get_or_create(
        doc=doc_limpo,
        defaults={
            'nome': nome,
            'telefone': telefone.replace('(', '').replace(')', '').replace(' ', '').replace('-', ''),
            'email': email,
            'tipo_doc': 'CPF' if len(doc_limpo) == 11 else 'CNPJ'
        }
    )
    
    if not created:
        pessoa.nome = nome
        pessoa.telefone = telefone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        pessoa.email = email
        pessoa.save()
    
    return pessoa


def get_or_create_promotor(user):
    """Obtém ou cria o promotor (pessoa do usuário)"""
    if hasattr(user, 'pessoa'):
        return user.pessoa
    
    promotor = Pessoa.objects.create(
        nome=user.get_full_name() or user.username,
        doc='00000000000',
        tipo_doc='CPF',
        email=user.email or f'{user.username}@gruporom.com.br'
    )
    user.pessoa = promotor
    user.save()
    
    return promotor


def create_caravana(data, promotor, responsavel):
    """Cria a caravana"""
    return Caravana.objects.create(
        nome=data.get('nome'),
        empresa_id=data.get('empresa'),
        promotor=promotor,
        responsavel=responsavel,
        tipo=data.get('tipo'),
        quantidade=int(data.get('quantidade', 0)),
        free_economica=int(data.get('free_economica', 0)),
        free_executiva=int(data.get('free_executiva', 0)),
        data_contrato=data.get('data_contrato'),
        repasse_valor=data.get('repasse_valor', 0),
        repasse_tipo=data.get('repasse_tipo'),
        link=data.get('link', ''),
    )


def process_lideres(caravana, lideres_data):
    """Processa e adiciona líderes à caravana"""
    lideres_objects = []
    
    for lider_data in lideres_data:
        if lider_data.get('doc'):
            lider = create_or_update_pessoa(
                doc=lider_data.get('doc', ''),
                nome=lider_data.get('nome', ''),
                telefone=lider_data.get('celular', ''),
                email=lider_data.get('email', '')
            )
            lideres_objects.append(lider)
    
    if lideres_objects:
        caravana.lideres.set(lideres_objects)


def create_initial_bloqueio(caravana, data):
    """Cria o bloqueio inicial para a caravana"""
    if not data.get('data_saida'):
        return
    
    bloqueio = Bloqueio.objects.create(
        caravana=caravana,
        descricao=f"Bloqueio {caravana.nome}",
        saida=data.get('data_saida'),
        valor=data.get('valor', 0),
        taxas=data.get('taxas', 0),
        moeda_valor=data.get('moeda', 'Real'),
        moeda_taxas=data.get('moeda_taxas', data.get('moeda', 'Real')),
        terrestre=False,
        ativo=True
    )
    
    paises_ids = data.get('paises', [])
    if paises_ids:
        bloqueio.paises.set(paises_ids)