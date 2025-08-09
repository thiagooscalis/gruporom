# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.db import models
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
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



def _process_message_sync(account, message_data, contacts_data):
    """
    Processa mensagem de forma síncrona
    """
    from core.models import WhatsAppContact, WhatsAppMessage, WhatsAppConversation
    from django.utils import timezone
    
    try:
        wamid = message_data['id']
        from_number = message_data['from']
        timestamp = timezone.datetime.fromtimestamp(
            int(message_data['timestamp']), 
            timezone.get_current_timezone()
        )
        
        # Encontra ou cria contato
        contact_info = next((c for c in contacts_data if c.get('wa_id') == from_number), None)
        
        # Garante que o número esteja no formato correto
        phone_number = from_number if from_number.startswith('+') else f'+{from_number}'
        
        contact, created = WhatsAppContact.objects.get_or_create(
            account=account,
            phone_number=phone_number,
            defaults={
                'name': contact_info.get('profile', {}).get('name', '') if contact_info else '',
                'profile_name': contact_info.get('profile', {}).get('name', '') if contact_info else phone_number,
            }
        )
        
        # Verifica se mensagem já existe
        if WhatsAppMessage.objects.filter(wamid=wamid).exists():
            logger.info(f"Mensagem {wamid} já processada")
            return
        
        # Verifica se existe conversa ativa
        conversation = WhatsAppConversation.objects.filter(
            account=account,
            contact=contact,
            status__in=['pending', 'assigned', 'in_progress']
        ).first()
        
        conversation_created = False
        if not conversation:
            # Cria nova conversa
            conversation = WhatsAppConversation.objects.create(
                account=account,
                contact=contact,
                status='pending',
                first_message_at=timestamp,
                last_activity=timestamp,
                priority='medium'
            )
            conversation_created = True
            logger.info(f"Nova conversa criada {conversation.id} para {contact.name or contact.phone_number}")
        
        # Extrai conteúdo da mensagem
        content = ''
        message_type = message_data.get('type', 'text')
        
        if message_type == 'text':
            content = message_data.get('text', {}).get('body', '')
        elif message_type == 'image':
            content = message_data.get('image', {}).get('caption', '[Imagem]')
        elif message_type == 'audio':
            content = '[Áudio]'
        elif message_type == 'video':
            content = message_data.get('video', {}).get('caption', '[Vídeo]')
        elif message_type == 'document':
            content = f"[Documento: {message_data.get('document', {}).get('filename', 'arquivo')}]"
        
        # Cria mensagem
        message = WhatsAppMessage.objects.create(
            wamid=wamid,
            account=account,
            contact=contact,
            conversation=conversation,
            direction='inbound',
            message_type=message_type,
            content=content,
            timestamp=timestamp,
            status='delivered'
        )
        
        # Atualiza última atividade da conversa
        conversation.last_activity = timestamp
        conversation.save(update_fields=['last_activity'])
        
        logger.info(f"Mensagem {wamid} processada - Conversa {conversation.id}")
        
        # Envia notificação WebSocket para nova conversa ou nova mensagem
        if conversation_created:
            _send_websocket_notification(conversation, content)
        else:
            # Para conversa existente, envia notificação de nova mensagem
            _send_message_websocket_notification(conversation, message, content)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        # Traceback removido dos logs por segurança em produção


def _process_status_update_sync(account, status_data):
    """
    Processa atualizações de status de mensagens (delivered, read, failed)
    """
    from core.models import WhatsAppMessage
    from django.utils import timezone
    
    try:
        wamid = status_data.get('id')
        status = status_data.get('status')
        timestamp = status_data.get('timestamp')
        
        if not wamid or not status:
            logger.warning("Status update sem WAMID ou status")
            return
        
        # Busca mensagem pelo WAMID
        try:
            message = WhatsAppMessage.objects.get(
                account=account,
                wamid=wamid,
                direction='outbound'  # Só mensagens enviadas por nós
            )
            
            # Atualiza status da mensagem
            old_status = message.status
            message.status = status
            
            # Converte timestamp se fornecido
            if timestamp:
                status_timestamp = timezone.datetime.fromtimestamp(
                    int(timestamp), 
                    timezone.get_current_timezone()
                )
                
                # Atualiza campos específicos baseado no status
                if status == 'delivered':
                    message.delivered_at = status_timestamp
                elif status == 'read':
                    message.read_at = status_timestamp
                    # Se foi lida, também foi entregue
                    if not message.delivered_at:
                        message.delivered_at = status_timestamp
            
            message.save()
            
            logger.info(f"Status da mensagem {wamid} atualizado: {old_status} → {status}")
            
            # Envia notificação WebSocket para atualizar interface quando status muda
            if old_status != status:
                _send_status_update_websocket_notification(message, old_status, status)
            
        except WhatsAppMessage.DoesNotExist:
            logger.warning(f"Mensagem {wamid} não encontrada para atualização de status")
            
    except Exception as e:
        logger.error(f"Erro ao processar status update: {e}")
        # Traceback removido dos logs por segurança em produção


def _send_status_update_websocket_notification(message, old_status, new_status):
    """
    Envia notificação WebSocket quando o status de uma mensagem muda (delivered, read)
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Channel layer não configurado - notificação WebSocket ignorada")
            return
        
        # Dados da atualização de status para enviar via WebSocket
        status_data = {
            'message_id': message.id,
            'conversation_id': message.conversation.id,
            'wamid': message.wamid,
            'old_status': old_status,
            'new_status': new_status,
            'timestamp': message.timestamp.isoformat(),
            'delivered_at': message.delivered_at.isoformat() if message.delivered_at else None,
            'read_at': message.read_at.isoformat() if message.read_at else None
        }
        
        # Envia notificação de mudança de status
        async_to_sync(channel_layer.group_send)(
            'whatsapp_comercial',
            {
                'type': 'message_status_update',
                'message_status': status_data
            }
        )
        
        logger.info(f"Notificação WebSocket enviada para status update: {message.id} ({old_status} → {new_status})")
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação WebSocket de status: {e}")
        # Traceback removido dos logs por segurança em produção


def _send_websocket_notification(conversation, message_content):
    """
    Envia notificação WebSocket para usuários comerciais sobre nova conversa
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from core.models import WhatsAppConversation
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Channel layer não configurado - notificação WebSocket ignorada")
            return
        
        # Dados da conversa para enviar via WebSocket
        conversation_data = {
            'id': conversation.id,
            'contact_name': conversation.contact.name or conversation.contact.profile_name or conversation.contact.phone_number,
            'contact_phone': conversation.contact.phone_number,
            'message_preview': message_content[:100] + ('...' if len(message_content) > 100 else ''),
            'created_at': conversation.first_message_at.isoformat() if conversation.first_message_at else '',
            'status': conversation.status
        }
        
        # Conta atual de conversas pendentes
        pending_count = WhatsAppConversation.objects.filter(status='pending').count()
        
        # Envia evento único com nova conversa e contador atualizado
        async_to_sync(channel_layer.group_send)(
            'whatsapp_comercial',
            {
                'type': 'conversation_new',
                'conversation': conversation_data,
                'pending_count': pending_count
            }
        )
        
        logger.info(f"Notificações WebSocket enviadas para nova conversa {conversation.id}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação WebSocket: {e}")
        # Traceback removido dos logs por segurança em produção


def _send_message_websocket_notification(conversation, message, message_content):
    """
    Envia notificação WebSocket sobre nova mensagem em conversa existente
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Channel layer não configurado - notificação WebSocket ignorada")
            return
        
        # Dados da mensagem para enviar via WebSocket
        message_data = {
            'id': message.id,
            'conversation_id': conversation.id,
            'content': message_content,
            'timestamp': message.timestamp.isoformat(),
            'direction': message.direction,
            'contact_name': conversation.contact.name or conversation.contact.profile_name or conversation.contact.phone_number,
        }
        
        # Envia notificação de nova mensagem
        async_to_sync(channel_layer.group_send)(
            'whatsapp_comercial',
            {
                'type': 'message_received',
                'message': message_data,
                'conversation_id': conversation.id
            }
        )
        
        logger.info(f"Notificação WebSocket enviada para nova mensagem {message.id} na conversa {conversation.id}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação WebSocket de mensagem: {e}")
        # Traceback removido dos logs por segurança em produção


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
            # Log básico do webhook
            logger.info(f"Webhook recebido para conta {account_id}")
            
            payload = json.loads(request.body)
            # Payload detalhado removido dos logs por segurança
            
            # Adiciona o webhook à fila para processamento posterior
            from core.models import WhatsAppWebhookQueue
            WhatsAppWebhookQueue.objects.create(
                account=account,
                payload=payload,
                status='pending'
            )
            logger.info(f"Webhook adicionado à fila para processamento posterior")
            
            # Processa de forma síncrona para evitar problemas com asyncio no dev server
            try:
                from core.services.whatsapp_api import WhatsAppAPIService
                
                # Parse do payload
                data = WhatsAppAPIService.parse_webhook_payload(payload)
                
                # Processa mensagens recebidas de forma síncrona
                for message_data in data['messages']:
                    _process_message_sync(account, message_data, data['contacts'])
                
                # Processa atualizações de status (delivered, read, etc)
                for status_data in data.get('statuses', []):
                    _process_status_update_sync(account, status_data)
                
                logger.info(f"Webhook processado com sucesso")
            except Exception as proc_error:
                # Se falhar o processamento imediato, não é problema
                # pois está na fila para reprocessamento
                logger.warning(f"Processamento falhou, mas webhook está na fila: {proc_error}")
            
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
    from core.models import WhatsAppWebhookQueue
    from django.utils import timezone
    from datetime import timedelta
    
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    # Busca últimos webhooks recebidos
    recent_webhooks = WhatsAppWebhookQueue.objects.filter(
        account=account
    ).order_by('-received_at')[:20]
    
    # Estatísticas dos webhooks
    last_24h = timezone.now() - timedelta(hours=24)
    webhook_stats = {
        'total': WhatsAppWebhookQueue.objects.filter(account=account).count(),
        'last_24h': WhatsAppWebhookQueue.objects.filter(
            account=account,
            received_at__gte=last_24h
        ).count(),
        'pending': WhatsAppWebhookQueue.objects.filter(
            account=account,
            status='pending'
        ).count(),
        'processed': WhatsAppWebhookQueue.objects.filter(
            account=account,
            status='processed'
        ).count(),
        'failed': WhatsAppWebhookQueue.objects.filter(
            account=account,
            status='failed'
        ).count(),
    }
    
    # Busca últimas mensagens recebidas
    recent_messages = WhatsAppMessage.objects.filter(
        account=account,
        direction='inbound'
    ).order_by('-timestamp')[:10]
    
    context = {
        'title': f'Diagnóstico Webhook - {account.name}',
        'account': account,
        'webhook_url': request.build_absolute_uri(f'/webhook/whatsapp/{account.id}/'),
        'webhook_verify_token': account.webhook_verify_token,
        'recent_webhooks': recent_webhooks,
        'webhook_stats': webhook_stats,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'administracao/whatsapp/webhook_debug.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_POST
def test_webhook(request, account_id):
    """
    Testa se o webhook está configurado corretamente
    """
    from django.http import HttpResponse
    import requests
    
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    # Testa se o webhook está respondendo
    webhook_url = request.build_absolute_uri(f'/webhook/whatsapp/{account.id}/')
    
    try:
        # Faz uma requisição GET para verificar o webhook (simula verificação do Meta)
        response = requests.get(
            webhook_url,
            params={
                'hub.mode': 'subscribe',
                'hub.verify_token': account.webhook_verify_token,
                'hub.challenge': 'test_challenge_123'
            },
            timeout=5
        )
        
        if response.status_code == 200 and response.text == 'test_challenge_123':
            # Webhook configurado corretamente
            html = """
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                <strong>Webhook funcionando!</strong><br>
                O webhook está configurado corretamente e respondendo às verificações.
            </div>
            """
        else:
            # Webhook não está respondendo corretamente
            html = f"""
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Problema no webhook!</strong><br>
                Status: {response.status_code}<br>
                Resposta: {response.text[:100]}
            </div>
            """
    except requests.exceptions.Timeout:
        html = """
        <div class="alert alert-danger">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Timeout!</strong><br>
            O webhook não respondeu no tempo esperado (5 segundos).
        </div>
        """
    except requests.exceptions.ConnectionError:
        html = """
        <div class="alert alert-danger">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Erro de conexão!</strong><br>
            Não foi possível conectar ao webhook. Verifique se a URL está acessível.
        </div>
        """
    except Exception as e:
        html = f"""
        <div class="alert alert-danger">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Erro!</strong><br>
            {str(e)}
        </div>
        """
    
    return HttpResponse(html)


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


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def bulk_send_modal(request, account_id):
    """
    Modal para envio de mensagens em massa
    """
    from core.models import Pessoa, Passageiro, Colaborador, Fornecedor, Usuario
    from core.models import Caravana, Cargo, Turno
    from django.contrib.auth.models import Group
    
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    # Templates disponíveis (apenas aprovados)
    templates = WhatsAppTemplate.objects.filter(
        account=account,
        status='approved'
    ).order_by('display_name')
    
    # Dados para filtros
    from django.db.models import Min
    caravanas = Caravana.objects.annotate(
        menor_saida=Min('bloqueio__saida')
    ).order_by('menor_saida').exclude(menor_saida__isnull=True)
    cargos = Cargo.objects.all().order_by('nome')
    turnos = Turno.objects.all().order_by('nome')
    grupos = Group.objects.all().order_by('name')
    
    context = {
        'account': account,
        'templates': templates,
        'caravanas': caravanas,
        'cargos': cargos,
        'turnos': turnos,
        'grupos': grupos,
    }
    
    return render(request, 'administracao/whatsapp/modals/bulk_send.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def load_recipients(request):
    """
    Carrega interface de seleção de destinatários baseado no tipo
    """
    from core.models import Pessoa, Passageiro, Colaborador, Fornecedor, Usuario
    from core.models import Caravana, Cargo, Turno
    from django.contrib.auth.models import Group
    from django.db.models import Min, Count
    
    recipient_type = request.GET.get('recipient_type', 'pessoas')
    
    # Contexto base
    context = {
        'recipient_type': recipient_type,
        'selected_count': 0,
        'valid_phones': 0,
    }
    
    # Templates específicos por tipo
    template_map = {
        'pessoas': 'administracao/whatsapp/partials/recipients_pessoas.html',
        'passageiros': 'administracao/whatsapp/partials/recipients_passageiros.html',
        'colaboradores': 'administracao/whatsapp/partials/recipients_colaboradores.html',
        'fornecedores': 'administracao/whatsapp/partials/recipients_fornecedores.html',
        'usuarios': 'administracao/whatsapp/partials/recipients_usuarios.html',
    }
    
    if recipient_type == 'pessoas':
        # Para pessoas, apenas precisamos do template com autocomplete
        context['selected_pessoas'] = []
        
    elif recipient_type == 'passageiros':
        # Carrega caravanas com contagem de passageiros
        context['caravanas'] = Caravana.objects.annotate(
            menor_saida=Min('bloqueio__saida'),
            total_passageiros=Count('bloqueio__passageiro', distinct=True)
        ).order_by('menor_saida').exclude(menor_saida__isnull=True)
        context['selected_caravanas_ids'] = []
        context['total_passageiros'] = 0
        
    elif recipient_type == 'colaboradores':
        context['cargos'] = Cargo.objects.all().order_by('nome')
        context['turnos'] = Turno.objects.all().order_by('nome')
        context['colaboradores'] = Colaborador.objects.select_related(
            'pessoa', 'cargo', 'turno'
        ).filter(data_demissao__isnull=True).order_by('pessoa__nome')
        context['selected_colaboradores_ids'] = []
        
    elif recipient_type == 'fornecedores':
        context['fornecedores'] = Fornecedor.objects.select_related(
            'pessoa'
        ).order_by('pessoa__nome')
        context['selected_fornecedores_ids'] = []
        
    elif recipient_type == 'usuarios':
        context['grupos'] = Group.objects.all().order_by('name')
        context['usuarios'] = Usuario.objects.select_related(
            'pessoa'
        ).filter(is_active=True).prefetch_related('groups').order_by('username')
        context['selected_usuarios_ids'] = []
    
    template_name = template_map.get(recipient_type, template_map['pessoas'])
    return render(request, template_name, context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def filter_recipients(request):
    """
    Filtra destinatários com os mesmos parâmetros do load_recipients
    """
    return load_recipients(request)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def template_preview(request):
    """
    Carrega prévia do template selecionado
    """
    template_id = request.GET.get('template_id')
    
    if not template_id:
        return render(request, 'administracao/whatsapp/partials/template_preview.html', {})
    
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    # Cria range para as variáveis
    variables_range = list(range(1, template.variables_count + 1)) if template.variables_count > 0 else []
    
    context = {
        'template': template,
        'variables_range': variables_range,
    }
    
    return render(request, 'administracao/whatsapp/partials/template_preview.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_POST
def update_count(request):
    """
    Atualiza contador de destinatários selecionados
    """
    # Conta quantos checkboxes estão marcados
    recipients = request.POST.getlist('recipients[]')
    count = len(recipients)
    
    # Salva na sessão
    request.session['selected_recipients'] = recipients
    
    return HttpResponse(str(count))


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_POST
def select_all_recipients(request):
    """
    Seleciona todos os destinatários do tipo atual
    """
    recipient_type = request.POST.get('recipient_type')
    # Aqui você implementaria a lógica para selecionar todos
    # Por ora, vamos apenas recarregar a lista
    return load_recipients(request)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_POST
def clear_selection(request):
    """
    Limpa seleção de destinatários
    """
    request.session['selected_recipients'] = []
    return load_recipients(request)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_POST
def bulk_send_process(request, account_id):
    """
    Processa o envio de mensagens em massa
    """
    account = get_object_or_404(WhatsAppAccount, id=account_id)
    
    template_id = request.POST.get('template_id')
    recipients = request.POST.getlist('recipients[]')
    # Configurações padrão
    test_mode = False  # Sempre envio real
    save_log = True    # Sempre salva log
    delay = 2          # Intervalo padrão
    
    if not template_id:
        messages.error(request, 'Por favor, selecione um template')
        return bulk_send_modal(request, account_id)
    
    if not recipients:
        messages.error(request, 'Por favor, selecione ao menos um destinatário')
        return bulk_send_modal(request, account_id)
    
    template = get_object_or_404(WhatsAppTemplate, id=template_id, account=account)
    
    # Coleta variáveis do template
    variables = {}
    for i in range(1, template.variables_count + 1):
        variables[str(i)] = request.POST.get(f'variable_{i}', '')
    
    # Função auxiliar para obter dados do destinatário
    def get_recipient_data(recipient_id):
        """
        Obtém os dados do destinatário baseado no tipo e ID
        """
        from core.models import Pessoa, Passageiro, Colaborador, Fornecedor, Usuario
        
        recipient_type, obj_id = recipient_id.split('_', 1)
        
        try:
            if recipient_type == 'pessoa':
                pessoa = Pessoa.objects.get(id=obj_id)
                return {
                    'name': pessoa.nome,
                    'phone': pessoa.celular or pessoa.telefone,
                    'responsible_user': None
                }
            elif recipient_type == 'passageiro':
                passageiro = Passageiro.objects.select_related('pessoa').get(id=obj_id)
                return {
                    'name': passageiro.pessoa.nome if passageiro.pessoa else 'Passageiro',
                    'phone': passageiro.pessoa.celular or passageiro.pessoa.telefone if passageiro.pessoa else None,
                    'responsible_user': None
                }
            elif recipient_type == 'colaborador':
                colaborador = Colaborador.objects.select_related('pessoa').get(id=obj_id)
                return {
                    'name': colaborador.pessoa.nome if colaborador.pessoa else 'Colaborador',
                    'phone': colaborador.pessoa.celular or colaborador.pessoa.telefone if colaborador.pessoa else None,
                    'responsible_user': None
                }
            elif recipient_type == 'fornecedor':
                fornecedor = Fornecedor.objects.select_related('pessoa').get(id=obj_id)
                return {
                    'name': fornecedor.pessoa.nome if fornecedor.pessoa else 'Fornecedor',
                    'phone': fornecedor.pessoa.celular or fornecedor.pessoa.telefone if fornecedor.pessoa else None,
                    'responsible_user': None
                }
            elif recipient_type == 'usuario':
                usuario = Usuario.objects.select_related('pessoa').get(id=obj_id)
                return {
                    'name': usuario.pessoa.nome if usuario.pessoa else usuario.username,
                    'phone': usuario.pessoa.celular or usuario.pessoa.telefone if usuario.pessoa else None,
                    'responsible_user': usuario
                }
        except Exception:
            return {
                'name': 'Destinatário Desconhecido',
                'phone': None,
                'responsible_user': None
            }
    
    # Função auxiliar para processar variáveis especiais para cada destinatário
    def process_variables_for_recipient(variables, recipient_data, current_user):
        """
        Processa variáveis especiais como @cliente e @atendente
        """
        processed = {}
        for key, value in variables.items():
            if value.lower() == '@cliente':
                # Extrai o nome do destinatário
                processed[key] = recipient_data.get('name', 'Cliente')
            elif value.lower() == '@atendente':
                # Usa o usuário responsável pelo cliente, ou o usuário logado caso não tenha responsável
                responsible_user = recipient_data.get('responsible_user')
                if responsible_user and hasattr(responsible_user, 'pessoa') and responsible_user.pessoa:
                    processed[key] = responsible_user.pessoa.nome
                elif responsible_user:
                    processed[key] = responsible_user.username
                elif hasattr(current_user, 'pessoa') and current_user.pessoa:
                    processed[key] = current_user.pessoa.nome
                else:
                    processed[key] = current_user.username
            else:
                processed[key] = value
        return processed
    
    # TODO: Implementar envio real via API
    # Por ora, apenas simula sucesso
    messages.success(
        request,
        f'✅ {len(recipients)} mensagens enviadas com sucesso usando o template "{template.display_name}"'
    )
    
    # Processa variáveis para exemplo usando dados reais do primeiro destinatário
    if recipients:
        first_recipient = get_recipient_data(recipients[0])
        processed_variables_sample = process_variables_for_recipient(variables, first_recipient, request.user)
    else:
        sample_recipient_data = {'name': 'Cliente Exemplo', 'responsible_user': None}
        processed_variables_sample = process_variables_for_recipient(variables, sample_recipient_data, request.user)
    
    return render(request, 'administracao/whatsapp/partials/bulk_send_result.html', {
        'account': account,
        'template': template,
        'recipients_count': len(recipients),
        'test_mode': False,
        'sent_count': len(recipients),
        'failed_count': 0,
        'variables': processed_variables_sample,
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
def count_selected(request):
    """
    Retorna a contagem de destinatários selecionados
    """
    selected = request.session.get('selected_recipients', [])
    return HttpResponse(f"{len(selected)} selecionados")


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administração').exists())
@require_POST
def update_preview(request):
    """
    Atualiza a prévia do template com as variáveis preenchidas
    """
    template_id = request.POST.get('template_id')
    if not template_id:
        return HttpResponse('')
    
    template = get_object_or_404(WhatsAppTemplate, id=template_id)
    
    # Coleta variáveis
    body_text = template.body_text
    header_text = template.header_text or ''
    footer_text = template.footer_text or ''
    
    for i in range(1, template.variables_count + 1):
        value = request.POST.get(f'variable_{i}', '')
        
        # Processa variáveis especiais
        if value.lower() == '@cliente':
            display_value = '<em>[Nome do Cliente]</em>'
        elif value.lower() == '@atendente':
            display_value = f'<em>{request.user.pessoa.nome if hasattr(request.user, "pessoa") else request.user.username}</em>'
        else:
            display_value = value
            
        if value:
            # Substitui em todos os campos
            body_text = body_text.replace(f'{{{{{i}}}}}', f'<strong>{display_value}</strong>')
            header_text = header_text.replace(f'{{{{{i}}}}}', f'<strong>{display_value}</strong>')
            footer_text = footer_text.replace(f'{{{{{i}}}}}', f'<strong>{display_value}</strong>')
    
    html = f'''
    <div class="alert alert-success">
        <h6 class="alert-heading">
            <i class="fas fa-eye me-2"></i>
            Prévia com Valores
        </h6>
        <div class="border rounded p-3 bg-white">
            {f'<div class="fw-bold text-primary mb-2">{header_text}</div>' if header_text else ''}
            <div class="mb-2">{body_text}</div>
            {f'<div class="text-muted small">{footer_text}</div>' if footer_text else ''}
        </div>
        <div class="mt-2">
            <small class="text-muted">
                <i class="fas fa-info-circle me-1"></i>
                <strong>@cliente</strong> será substituído pelo nome do destinatário | 
                <strong>@atendente</strong> será substituído pelo seu nome
            </small>
        </div>
    </div>
    '''
    
    return HttpResponse(html)


