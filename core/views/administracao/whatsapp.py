# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.db import models
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging

from core.models import WhatsAppAccount, WhatsAppContact, WhatsAppMessage, WhatsAppTemplate
from core.services.whatsapp_api import WhatsAppAPIService, WhatsAppWebhookProcessor
from core.forms.whatsapp import WhatsAppAccountForm, WhatsAppAccountTestForm, WhatsAppTemplateForm

# Logger
logger = logging.getLogger(__name__)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def dashboard(request):
    """
    Dashboard principal do WhatsApp
    """
    # Estatísticas gerais
    total_accounts = WhatsAppAccount.objects.filter(is_active=True).count()
    total_contacts = WhatsAppContact.objects.count()
    
    # Mensagens das últimas 24h
    yesterday = timezone.now() - timedelta(days=1)
    messages_24h = WhatsAppMessage.objects.filter(
        timestamp__gte=yesterday
    ).count()
    
    # Mensagens por direção nas últimas 24h
    inbound_24h = WhatsAppMessage.objects.filter(
        timestamp__gte=yesterday,
        direction='inbound'
    ).count()
    
    outbound_24h = WhatsAppMessage.objects.filter(
        timestamp__gte=yesterday,
        direction='outbound'
    ).count()
    
    # Contas ativas
    active_accounts = WhatsAppAccount.objects.filter(
        is_active=True,
        status='active'
    ).select_related('responsavel')
    
    # Mensagens recentes
    recent_messages = WhatsAppMessage.objects.select_related(
        'account', 'contact', 'sent_by'
    ).order_by('-timestamp')[:10]
    
    # Templates recentes (últimos 5)
    templates = WhatsAppTemplate.objects.select_related('account').order_by('-criado_em')[:5]
    
    context = {
        'total_accounts': total_accounts,
        'total_contacts': total_contacts,
        'messages_24h': messages_24h,
        'inbound_24h': inbound_24h,
        'outbound_24h': outbound_24h,
        'active_accounts': active_accounts,
        'recent_messages': recent_messages,
        'templates': templates,
    }
    
    return render(request, 'administracao/whatsapp/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def accounts_list(request):
    """
    Lista de contas WhatsApp
    """
    # Busca
    search = request.GET.get('search', '')
    
    # Query base
    accounts = WhatsAppAccount.objects.select_related('responsavel')
    
    # Aplica filtro de busca
    if search:
        accounts = accounts.filter(
            Q(name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(responsavel__username__icontains=search)
        )
    
    # Ordenação
    accounts = accounts.order_by('name')
    
    # Paginação
    paginator = Paginator(accounts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'administracao/whatsapp/accounts_list.html', context)




@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request, account_id):
    """
    Webhook para receber notificações do WhatsApp
    """
    try:
        account = WhatsAppAccount.objects.get(id=account_id, is_active=True)
    except WhatsAppAccount.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        # Verificação do webhook
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and WhatsAppAPIService.verify_webhook(token, account.webhook_verify_token):
            logger.info(f"Webhook verificado com sucesso para conta {account_id}")
            return HttpResponse(challenge)
        else:
            logger.warning(f"Falha na verificação do webhook para conta {account_id}")
            return HttpResponse(status=403)
    
    elif request.method == 'POST':
        # Processamento do webhook
        try:
            # Log detalhado para debug
            logger.info(f"=== WEBHOOK RECEBIDO ===")
            logger.info(f"Conta ID: {account_id}")
            logger.info(f"Headers: {dict(request.headers)}")
            logger.info(f"Body bruto: {request.body.decode('utf-8')}")
            
            payload = json.loads(request.body)
            logger.info(f"Payload JSON: {payload}")
            
            # Processa webhook de forma assíncrona
            processor = WhatsAppWebhookProcessor(account)
            # TODO: Processar de forma assíncrona usando Celery ou similar
            # Por enquanto, processa síncronamente
            import asyncio
            result = asyncio.run(processor.process_webhook(payload))
            
            logger.info(f"Webhook processado com sucesso: {result}")
            return HttpResponse(status=200)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON do webhook: {e}")
            logger.error(f"Body recebido: {request.body}")
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return HttpResponse(status=500)
    
    return HttpResponse(status=405)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def webhook_debug(request, account_id):
    """
    View para debug do webhook - mostra informações da conta e testa conectividade
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    debug_info = {
        'account_info': {
            'id': account.id,
            'name': account.name,
            'phone_number': account.phone_number,
            'phone_number_id': account.phone_number_id,
            'business_account_id': account.business_account_id,
            'access_token': account.access_token[:20] + '...' if account.access_token else None,
            'webhook_verify_token': account.webhook_verify_token,
            'is_active': account.is_active,
            'status': account.get_status_display(),
        },
        'webhook_url': request.build_absolute_uri(f'/webhook/whatsapp/{account.id}/'),
        'recent_messages': list(WhatsAppMessage.objects.filter(
            account=account
        ).order_by('-timestamp')[:5].values(
            'direction', 'message_type', 'content', 'status', 'timestamp'
        )),
        'webhook_logs': []  # TODO: Implementar logs específicos do webhook
    }
    
    # Testa API do WhatsApp
    try:
        api_service = WhatsAppAPIService(account)
        # TODO: Implementar teste de conectividade
        debug_info['api_status'] = 'OK'
    except Exception as e:
        debug_info['api_status'] = f'Erro: {str(e)}'
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})


# ==================== VIEWS DE TEMPLATES ====================

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def templates_list(request, account_id):
    """
    Lista de templates de uma conta
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    # Busca
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    # Query base
    templates = WhatsAppTemplate.objects.filter(account=account)
    
    # Filtros
    if search:
        templates = templates.filter(
            Q(display_name__icontains=search) |
            Q(name__icontains=search) |
            Q(body_text__icontains=search)
        )
    
    if status_filter:
        templates = templates.filter(status=status_filter)
    
    if category_filter:
        templates = templates.filter(category=category_filter)
    
    # Paginação
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total': templates.count(),
        'approved': templates.filter(status='approved').count(),
        'pending': templates.filter(status='pending').count(),
        'rejected': templates.filter(status='rejected').count(),
    }
    
    context = {
        'area': 'administracao',  # Adiciona a área para o menu
        'account': account,
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'stats': stats,
        'status_choices': WhatsAppTemplate.TEMPLATE_STATUS_CHOICES,
        'category_choices': WhatsAppTemplate.TEMPLATE_CATEGORY_CHOICES,
    }
    
    return render(request, 'administracao/whatsapp/templates_list.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def template_create_modal(request):
    """
    Modal para criar template
    """
    if request.method == 'POST':
        form = WhatsAppTemplateForm(request.POST, user=request.user)
        if form.is_valid():
            template = form.save()
            
            messages.success(request, f'Template "{template.display_name}" criado com sucesso!')
            
            response = HttpResponse()
            response['HX-Trigger'] = 'templateSaved'
            return response
        else:
            # Retorna o formulário com erros
            return render(request, 'administracao/whatsapp/modals/template_form.html', {
                'form': form,
                'title': 'Criar Template',
                'action_url': request.get_full_path(),
            })
    else:
        form = WhatsAppTemplateForm(user=request.user)
        
        return render(request, 'administracao/whatsapp/modals/template_form.html', {
            'form': form,
            'title': 'Criar Template',
            'action_url': request.get_full_path(),
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def template_edit_modal(request, template_id):
    """
    Modal para editar template
    """
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    if request.method == 'POST':
        form = WhatsAppTemplateForm(request.POST, instance=template, user=request.user)
        if form.is_valid():
            template = form.save()
            
            messages.success(request, f'Template "{template.display_name}" atualizado com sucesso!')
            
            response = HttpResponse()
            response['HX-Trigger'] = 'templateSaved'
            return response
        else:
            # Retorna o formulário com erros
            return render(request, 'administracao/whatsapp/modals/template_form.html', {
                'form': form,
                'template': template,
                'title': 'Editar Template',
                'action_url': request.get_full_path(),
            })
    else:
        form = WhatsAppTemplateForm(instance=template, user=request.user)
        
        return render(request, 'administracao/whatsapp/modals/template_form.html', {
            'form': form,
            'template': template,
            'title': 'Editar Template',  
            'action_url': request.get_full_path(),
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())  
def template_delete_modal(request, template_id):
    """
    Modal para excluir template
    """
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    if request.method == 'POST':
        template_name = template.display_name
        template.delete()
        
        messages.success(request, f'Template "{template_name}" excluído com sucesso!')
        
        response = HttpResponse()
        response['HX-Trigger'] = 'templateDeleted'
        return response
    
    return render(request, 'administracao/whatsapp/modals/template_delete.html', {
        'template': template,
        'action_url': request.get_full_path(),
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def template_preview_modal(request, template_id):
    """
    Modal para prévia do template
    """
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    # Exemplo de variáveis para preview
    sample_variables = []
    for i in range(1, 11):  # Máximo 10 variáveis
        var_display = f"{{{{{i}}}}}"  # Gera {{1}}, {{2}}, etc.
        var_values = [
            "João Silva", "50% de desconto", "hoje", "R$ 100,00", "www.exemplo.com",
            "Produto X", "amanhã", "código123", "15:30", "Grupo ROM"
        ]
        sample_variables.append({
            'number': i,
            'display': var_display,
            'value': var_values[i-1] if i <= len(var_values) else f"Valor {i}"
        })
    
    # Gera preview com variáveis substituídas
    preview_content = {
        'header': template.header_text,
        'body': template.body_text,
        'footer': template.footer_text,
    }
    
    # Substitui variáveis no preview
    import re
    for section, text in preview_content.items():
        if text:
            for variable in sample_variables:
                var_pattern = rf'\{{\{{{variable["number"]}\}}\}}'
                text = re.sub(var_pattern, str(variable["value"]), text)
            preview_content[section] = text
    
    return render(request, 'administracao/whatsapp/modals/template_preview.html', {
        'template': template,
        'preview_content': preview_content,
        'sample_variables': sample_variables,
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_http_methods(["POST"])
def template_submit_approval(request, template_id):
    """
    Submete um template para aprovação na API do WhatsApp
    """
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    # Verifica se o template já foi submetido
    if template.template_id:
        messages.warning(request, 'Este template já foi submetido para aprovação.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # Verifica se o template tem status pendente
    if template.status not in ['pending', 'rejected']:
        messages.warning(request, 'Este template não pode ser submetido no status atual.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    try:
        # Cria instância do serviço da API
        api_service = WhatsAppAPIService(template.account)
        
        # Submete o template para aprovação
        result = api_service.submit_template_for_approval(template)
        
        if result['success']:
            messages.success(
                request, 
                f'Template "{template.display_name}" enviado para aprovação com sucesso! '
                f'ID: {result.get("template_id", "N/A")}'
            )
        else:
            error_details = result.get('error_details', {}).get('error', {})
            error_msg = result.get('error_message', result.get('error'))
            error_code = result.get('error_code', '')
            error_subcode = error_details.get('error_subcode')
            
            # Mensagem específica para template duplicado
            if error_subcode == 2388024:
                user_msg = error_details.get('error_user_msg', '')
                messages.error(
                    request, 
                    f'❌ Template já existe: {user_msg}. Tente usar um nome diferente como: '
                    f'{template.name}_v2, {template.name}_2025, ou {template.name}_new'
                )
            elif error_code:
                messages.error(
                    request, 
                    f'❌ Erro ao enviar template: {error_msg} (Código: {error_code})'
                )
            else:
                messages.error(
                    request, 
                    f'❌ Erro ao enviar template para aprovação: {error_msg}'
                )
            
            # Log detalhado para debug
            logger.error(f"Erro completo da API: {result.get('error_details', {})}")
    
    except Exception as e:
        logger.error(f"Erro ao submeter template {template_id}: {e}")
        messages.error(request, f'Erro inesperado ao enviar template: {str(e)}')
    
    # Retorna para a página anterior ou lista de templates
    return HttpResponseRedirect(
        request.META.get('HTTP_REFERER', f'/administracao/whatsapp/templates/{template.account.id}/')
    )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def api_permissions_test(request, account_id):
    """
    Testa as permissões da API do WhatsApp para uma conta
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    try:
        # Cria instância do serviço da API
        api_service = WhatsAppAPIService(account)
        
        # Executa testes de permissão
        result = api_service.test_api_permissions()
        
        context = {
                'account': account,
            'test_result': result,
            'tests': result.get('tests', [])
        }
        
        return render(request, 'administracao/whatsapp/modals/api_test_results.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao testar permissões da API para conta {account_id}: {e}")
        return JsonResponse({
            'error': f'Erro ao testar permissões: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_http_methods(["POST"])
def template_check_status(request, template_id):
    """
    Verifica o status de um template na API do WhatsApp
    """
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    if not template.template_id and not template.name:
        messages.warning(request, 'Este template ainda não foi submetido para aprovação.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    try:
        # Cria instância do serviço da API
        api_service = WhatsAppAPIService(template.account)
        
        # Atualiza o status do template
        result = api_service.update_template_status(template)
        
        if result['success']:
            if result['updated']:
                old_status = result.get('old_status', '')
                new_status = result.get('new_status', '')
                
                if new_status == 'approved':
                    messages.success(
                        request, 
                        f'✅ Template aprovado! Status: {old_status} → {template.get_status_display()}'
                    )
                elif new_status == 'rejected':
                    rejection_reason = result.get('rejection_reason', 'Motivo não especificado')
                    messages.error(
                        request, 
                        f'❌ Template rejeitado. Status: {old_status} → {template.get_status_display()}. '
                        f'Motivo: {rejection_reason}'
                    )
                else:
                    messages.info(
                        request, 
                        f'📋 Status atualizado: {old_status} → {template.get_status_display()}'
                    )
            else:
                current_status = result.get('current_status', template.status)
                messages.info(
                    request, 
                    f'ℹ️ Status atual: {template.get_status_display()}. Nenhuma mudança detectada.'
                )
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            messages.error(request, f'❌ Erro ao verificar status: {error_msg}')
    
    except Exception as e:
        logger.error(f"Erro ao verificar status do template {template_id}: {e}")
        messages.error(request, f'Erro ao verificar status: {str(e)}')
    
    return HttpResponseRedirect(
        request.META.get('HTTP_REFERER', f'/administracao/whatsapp/templates/{template.account.id}/')
    )


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def contacts_list(request, account_id):
    """
    Lista de contatos de uma conta
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    # Busca
    search = request.GET.get('search', '')
    
    # Query base
    contacts = WhatsAppContact.objects.filter(account=account)
    
    # Aplica filtro de busca
    if search:
        contacts = contacts.filter(
            Q(name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(profile_name__icontains=search)
        )
    
    # Anota com estatísticas
    contacts = contacts.annotate(
        total_messages=Count('messages'),
        last_message_time=models.Max('messages__timestamp')
    ).order_by('-last_message_time')
    
    # Paginação
    paginator = Paginator(contacts, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'account': account,
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'administracao/whatsapp/contacts_list.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def messages_list(request):
    """
    Lista de todas as mensagens
    """
    # Filtros
    account_id = request.GET.get('account')
    direction = request.GET.get('direction')
    message_type = request.GET.get('type')
    status = request.GET.get('status')
    search = request.GET.get('search', '')
    
    # Query base
    messages = WhatsAppMessage.objects.select_related(
        'account', 'contact', 'sent_by'
    )
    
    # Aplica filtros
    if account_id:
        messages = messages.filter(account_id=account_id)
    
    if direction:
        messages = messages.filter(direction=direction)
    
    if message_type:
        messages = messages.filter(message_type=message_type)
    
    if status:
        messages = messages.filter(status=status)
    
    if search:
        messages = messages.filter(
            Q(content__icontains=search) |
            Q(contact__name__icontains=search) |
            Q(contact__phone_number__icontains=search)
        )
    
    # Ordenação
    messages = messages.order_by('-timestamp')
    
    # Paginação
    paginator = Paginator(messages, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    accounts = WhatsAppAccount.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'accounts': accounts,
        'filters': {
            'account': account_id,
            'direction': direction,
            'type': message_type,
            'status': status,
            'search': search,
        },
        'direction_choices': WhatsAppMessage.DIRECTION_CHOICES,
        'type_choices': WhatsAppMessage.MESSAGE_TYPE_CHOICES,
        'status_choices': WhatsAppMessage.MESSAGE_STATUS_CHOICES,
    }
    
    return render(request, 'administracao/whatsapp/messages_list.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def account_create_modal(request):
    """
    Modal para criar nova conta WhatsApp
    """
    if request.method == 'POST':
        form = WhatsAppAccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Conta WhatsApp "{account.name}" criada com sucesso!')
            response = HttpResponse()
            response['HX-Trigger'] = 'whatsappAccountSaved'
            return response
    else:
        form = WhatsAppAccountForm()
    
    return render(request, 'administracao/whatsapp/modals/account_form.html', {
        'form': form,
        'title': 'Nova Conta WhatsApp',
        'action_url': request.path
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def account_edit_modal(request, account_id):
    """
    Modal para editar conta WhatsApp
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    if request.method == 'POST':
        form = WhatsAppAccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Conta WhatsApp "{account.name}" atualizada com sucesso!')
            response = HttpResponse()
            response['HX-Trigger'] = 'whatsappAccountSaved'
            return response
    else:
        form = WhatsAppAccountForm(instance=account)
    
    return render(request, 'administracao/whatsapp/modals/account_form.html', {
        'form': form,
        'account': account,
        'title': f'Editar Conta - {account.name}',
        'action_url': request.path
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def account_delete_modal(request, account_id):
    """
    Modal para excluir conta WhatsApp
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    if request.method == 'POST':
        try:
            account_name = account.name
            
            # Verifica se há mensagens relacionadas
            messages_count = WhatsAppMessage.objects.filter(account=account).count()
            contacts_count = WhatsAppContact.objects.filter(account=account).count()
            
            if messages_count > 0:
                messages.warning(
                    request, 
                    f'Não é possível excluir a conta "{account_name}" pois possui {messages_count} mensagens e {contacts_count} contatos relacionados. Desative a conta em vez de excluí-la.'
                )
                return JsonResponse({
                    'success': False,
                    'message': f'Conta possui {messages_count} mensagens relacionadas. Desative em vez de excluir.'
                })
            
            account.delete()
            messages.success(request, f'Conta WhatsApp "{account_name}" excluída com sucesso!')
            return JsonResponse({
                'success': True,
                'message': 'Conta excluída com sucesso!',
                'redirect': request.META.get('HTTP_REFERER', '/administracao/whatsapp/')
            })
            
        except Exception as e:
            logger.error(f"Erro ao excluir conta WhatsApp {account_id}: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erro interno. Tente novamente.'
            })
    
    # Calcula estatísticas para exibir no modal
    messages_count = WhatsAppMessage.objects.filter(account=account).count()
    contacts_count = WhatsAppContact.objects.filter(account=account).count()
    
    return render(request, 'administracao/whatsapp/modals/account_delete.html', {
        'account': account,
        'messages_count': messages_count,
        'contacts_count': contacts_count,
        'action_url': request.path
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def account_test_modal(request, account_id):
    """
    Modal para testar conectividade da conta WhatsApp
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    if request.method == 'POST':
        form = WhatsAppAccountTestForm(request.POST, account=account)
        if form.is_valid():
            test_phone = form.cleaned_data['test_phone_number']
            template = form.cleaned_data['template']
            
            try:
                # Testa conexão com a API
                api_service = WhatsAppAPIService(account)
                
                # Primeiro tenta obter perfil (teste mais leve)
                profile_result = api_service.get_business_profile()
                
                if not profile_result['success']:
                    return JsonResponse({
                        'success': False,
                        'message': f'Erro na conexão: {profile_result["error"]}'
                    })
                
                # Se perfil OK, simula envio de template de teste  
                # TODO: Implementar envio real de template na API
                
                # Gera valores de exemplo para as variáveis
                template_variables = []
                if template.variables_count > 0:
                    sample_values = [
                        "Cliente Teste", "Produto Demo", "50%", "hoje", 
                        "www.exemplo.com", "Código123", "15:30", "valor",
                        "desconto", "promoção"
                    ]
                    template_variables = sample_values[:template.variables_count]
                
                # Simula sucesso (em produção, usar API real de templates)
                fake_message_id = f"wamid_test_{template.id}_{hash(test_phone)}"
                
                messages.success(
                    request, 
                    f'Teste simulado com sucesso! Template "{template.display_name}" seria enviado para {test_phone}'
                )
                
                # Retorna template de sucesso
                return render(request, 'administracao/whatsapp/modals/test_success.html', {
                    'account': account,
                    'phone': test_phone,
                    'template': template,
                    'template_variables': template_variables,
                    'message_id': fake_message_id,
                    'profile': profile_result.get('data', {})
                })
                    
            except Exception as e:
                logger.error(f"Erro no teste da conta {account_id}: {e}")
                messages.error(request, f'Erro interno: {str(e)[:100]}')
    else:
        form = WhatsAppAccountTestForm(account=account)
    
    return render(request, 'administracao/whatsapp/modals/account_test.html', {
        'form': form,
        'account': account,
        'action_url': request.path
    })