# -*- coding: utf-8 -*-
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from core.models import (
    WhatsAppAccount, WhatsAppTemplate, WhatsAppConversation, 
    WhatsAppMessage, WhatsAppContact
)
from core.forms.whatsapp import NovoContatoForm, SendDocumentForm

logger = logging.getLogger(__name__)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists() and u.has_perm('core.controle_whatsapp'))
def whatsapp_geral(request):
    """
    Página WhatsApp Geral - visualiza todas as conversas de todos os atendentes
    """
    # Busca todas as conversas ordenadas por data de última atividade
    from django.db.models import Subquery, OuterRef
    
    # Subquery para buscar a última mensagem de cada conversa
    latest_message = WhatsAppMessage.objects.filter(
        conversation=OuterRef('pk')
    ).order_by('-timestamp').values('content')[:1]
    
    conversas = WhatsAppConversation.objects.select_related(
        'account', 'assigned_to', 'assigned_to__pessoa', 'contact'
    ).annotate(
        message_count=Count('messages'),
        last_message_content=Subquery(latest_message)
    ).order_by('-atualizado_em')
    
    # Filtros opcionais
    status_filter = request.GET.get('status', '')
    atendente_filter = request.GET.get('atendente', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        conversas = conversas.filter(status=status_filter)
    
    if atendente_filter:
        if atendente_filter == 'unassigned':
            conversas = conversas.filter(assigned_to__isnull=True)
        else:
            conversas = conversas.filter(assigned_to__id=atendente_filter)
    
    if search:
        conversas = conversas.filter(
            Q(contact__name__icontains=search) |
            Q(contact__profile_name__icontains=search) |
            Q(contact__phone_number__icontains=search) |
            Q(last_message_content__icontains=search)
        )
    
    # Estatísticas
    stats = {
        'total': WhatsAppConversation.objects.count(),
        'pending': WhatsAppConversation.objects.filter(status='pending').count(),
        'assigned': WhatsAppConversation.objects.filter(status='assigned').count(),
        'in_progress': WhatsAppConversation.objects.filter(status='in_progress').count(),
        'resolved': WhatsAppConversation.objects.filter(status='resolved').count(),
    }
    
    # Lista de atendentes para filtro
    from django.contrib.auth import get_user_model
    User = get_user_model()
    atendentes = User.objects.filter(
        groups__name='Comercial',
        whatsapp_conversations__isnull=False
    ).distinct().select_related('pessoa')
    
    context = {
        'title': 'WhatsApp Geral',
        'conversas': conversas,
        'stats': stats,
        'atendentes': atendentes,
        'status_filter': status_filter,
        'atendente_filter': atendente_filter,
        'search': search,
        'status_choices': WhatsAppConversation.STATUS_CHOICES,
    }
    
    return render(request, 'comercial/whatsapp/geral.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def test_websocket(request):
    """
    Debug endpoint para testar WebSocket manualmente
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if not channel_layer:
            return JsonResponse({
                'success': False,
                'error': 'Channel layer não configurado'
            })
        
        # Envia mensagem de teste
        test_data = {
            'id': 999,
            'contact_name': 'TESTE WebSocket',
            'contact_phone': '+5511999999999',
            'message_preview': '🧪 Esta é uma mensagem de teste do WebSocket!',
            'created_at': timezone.now().isoformat(),
            'status': 'pending'
        }
        
        # Conta atual de conversas pendentes
        pending_count = WhatsAppConversation.objects.filter(status='pending').count()
        
        # Envia via WebSocket
        async_to_sync(channel_layer.group_send)(
            'whatsapp_comercial',
            {
                'type': 'conversation_new',
                'conversation': test_data,
                'pending_count': pending_count
            }
        )
        
        logger.info("🧪 Mensagem de teste WebSocket enviada")
        
        return JsonResponse({
            'success': True,
            'message': 'Mensagem de teste enviada via WebSocket',
            'data': test_data,
            'pending_count': pending_count
        })
        
    except Exception as e:
        logger.error(f"Erro no teste WebSocket: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def dashboard(request):
    """
    Dashboard do WhatsApp comercial - Layout de chat completo
    """
    # Conversas serão carregadas via HTMX (my_conversations view)
    
    # Conversas pendentes (para o modal)
    pending_conversations = WhatsAppConversation.objects.filter(
        status='pending'
    ).select_related(
        'contact', 'account'
    ).annotate(
        messages_count=Count('messages')
    ).order_by('-last_activity')
    
    # Conversa selecionada (APENAS se especificada na URL - não abre automaticamente)
    selected_conversation_id = request.GET.get('conversation')
    selected_conversation = None
    messages = []
    
    if selected_conversation_id:
        try:
            selected_conversation = WhatsAppConversation.objects.select_related(
                'contact', 'account'
            ).get(
                id=selected_conversation_id,
                assigned_to=request.user,
                status__in=['assigned', 'in_progress']
            )
            # Mensagens da conversa selecionada
            messages = selected_conversation.messages.select_related(
                'contact'
            ).order_by('timestamp')
        except WhatsAppConversation.DoesNotExist:
            pass
    
    # Não abre conversa automaticamente - usuário deve clicar para escolher
    
    context = {
        'title': 'WhatsApp Business',
        'pending_count': pending_conversations.count(),
        'selected_conversation': selected_conversation,
        'messages': messages,
        'hide_messages': True,  # Oculta as mensagens do Django na página de chat
        'hide_padding': True,   # Remove padding para layout fullscreen
        # Breadcrumb
        'prev_page': 'Comercial',
        'prev_url': '/comercial/',
        'cur_page': 'WhatsApp Business',
    }
    
    return render(request, 'comercial/whatsapp/chat.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def conversations_table(request):
    """
    Retorna apenas a tabela de conversas para atualização via HTMX
    """
    # Conversas aguardando atendimento (pendentes)
    pending_conversations = WhatsAppConversation.objects.filter(
        status='pending'
    ).select_related(
        'contact', 'account'
    ).prefetch_related(
        'messages'
    ).annotate(
        messages_count=Count('messages'),
        unread_count=Count('messages', filter=Q(
            messages__direction='inbound',
            messages__status__in=['sent', 'delivered']
        ))
    ).order_by('-last_activity')
    
    context = {
        'pending_conversations': pending_conversations,
    }
    
    return render(request, 'comercial/whatsapp/partials/conversation_table.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def my_conversations(request):
    """
    Retorna lista de conversas do usuário (para atualização HTMX)
    """
    search = request.GET.get('search', '').strip()
    
    my_conversations_qs = WhatsAppConversation.objects.filter(
        assigned_to=request.user,
        status__in=['assigned', 'in_progress']
    ).select_related(
        'contact', 'account'
    ).prefetch_related(
        'messages'
    )
    
    # Aplica filtro de busca se fornecido
    if search:
        my_conversations_qs = my_conversations_qs.filter(
            Q(contact__name__icontains=search) |
            Q(contact__profile_name__icontains=search) |
            Q(contact__phone_number__icontains=search)
        )
    
    my_conversations = my_conversations_qs.annotate(
        messages_count=Count('messages'),
        unread_count=Count('messages', filter=Q(
            messages__direction='inbound',
            messages__status__in=['sent', 'delivered']
        ))
    ).order_by('-last_activity')
    
    selected_conversation_id = request.GET.get('conversation')
    selected_conversation = None
    if selected_conversation_id:
        try:
            selected_conversation = my_conversations.get(id=selected_conversation_id)
        except:
            pass
    
    context = {
        'my_conversations': my_conversations,
        'selected_conversation': selected_conversation,
    }
    
    return render(request, 'comercial/whatsapp/partials/contacts_list.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def pending_conversations(request):
    """
    Retorna conversas pendentes para o modal
    """
    pending_conversations = WhatsAppConversation.objects.filter(
        status='pending'
    ).select_related(
        'contact', 'account'
    ).prefetch_related(
        'messages'
    ).annotate(
        messages_count=Count('messages')
    ).order_by('-last_activity')
    
    return render(request, 'comercial/whatsapp/partials/pending_conversations.html', {
        'pending_conversations': pending_conversations
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def conversation_messages(request, conversation_id):
    """
    Retorna mensagens de uma conversa (para atualização HTMX)
    """
    conversation = get_object_or_404(
        WhatsAppConversation,
        id=conversation_id,
        assigned_to=request.user
    )
    
    messages = conversation.messages.select_related(
        'contact'
    ).order_by('timestamp')
    
    # Usa template sem script se for requisição HTMX
    template_name = 'comercial/whatsapp/partials/messages_clean.html' if request.headers.get('HX-Request') else 'comercial/whatsapp/partials/messages.html'
    return render(request, template_name, {
        'messages': messages
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def conversation_chat_area(request, conversation_id):
    """
    Retorna área de chat completa para uma conversa (para substituir apenas a área de chat)
    """
    conversation = get_object_or_404(
        WhatsAppConversation,
        id=conversation_id,
        assigned_to=request.user,
        status__in=['assigned', 'in_progress']
    )
    
    messages = conversation.messages.select_related(
        'contact'
    ).order_by('timestamp')
    
    context = {
        'selected_conversation': conversation,
        'messages': messages,
    }
    
    return render(request, 'comercial/whatsapp/partials/chat_area.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def conversation_messages_readonly(request, conversation_id):
    """
    Retorna mensagens de qualquer conversa (para visualização read-only no WhatsApp Geral)
    """
    conversation = get_object_or_404(
        WhatsAppConversation.objects.select_related(
            'contact', 'assigned_to', 'assigned_to__pessoa'
        ),
        id=conversation_id
    )
    
    messages = conversation.messages.select_related(
        'contact', 'sent_by', 'sent_by__pessoa'
    ).order_by('timestamp')
    
    return render(request, 'comercial/whatsapp/partials/messages_readonly.html', {
        'messages': messages,
        'conversation': conversation
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def pending_count(request):
    """
    Retorna contador de conversas pendentes (JSON)
    """
    count = WhatsAppConversation.objects.filter(status='pending').count()
    return JsonResponse({'count': count})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def check_24h_window(request):
    """
    Verifica se a conversa está dentro da janela de 24h do WhatsApp
    """
    conversation_id = request.POST.get('conversation_id')
    
    if not conversation_id:
        return JsonResponse({'error': 'ID da conversa não fornecido'}, status=400)
    
    try:
        conversation = get_object_or_404(
            WhatsAppConversation,
            id=conversation_id,
            assigned_to=request.user
        )
        
        within_window = conversation.is_within_24h_window()
        
        response_data = {
            'within_24h_window': within_window,
            'conversation_id': conversation_id
        }
        
        if not within_window:
            # Busca última mensagem recebida para mostrar no toast
            last_inbound = conversation.messages.filter(
                direction='inbound'
            ).order_by('-timestamp').first()
            
            if last_inbound:
                from django.utils import timezone
                time_diff = timezone.now() - last_inbound.timestamp
                hours_passed = int(time_diff.total_seconds() / 3600)
                response_data['hours_since_last_message'] = hours_passed
            
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Erro ao verificar janela de 24h: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def send_message(request):
    """
    Envia mensagem WhatsApp com sincronização API
    """
    import json
    data = json.loads(request.body)
    
    conversation_id = data.get('conversation_id')
    message_text = data.get('message')
    
    if not message_text or not message_text.strip():
        return JsonResponse({'success': False, 'error': 'Mensagem não pode estar vazia'})
    
    conversation = get_object_or_404(
        WhatsAppConversation,
        id=conversation_id,
        assigned_to=request.user
    )
    
    try:
        # Adiciona prefixo com área de acesso e nome do usuário
        area_nome = "COMERCIAL"  # Área comercial
        usuario_nome = request.user.pessoa.nome if hasattr(request.user, 'pessoa') and request.user.pessoa else request.user.username
        prefixo = f"[{area_nome}] - {usuario_nome}\n"
        mensagem_completa = prefixo + message_text.strip()
        
        # 1. Salva mensagem no banco primeiro com status 'sending'
        message = WhatsAppMessage.objects.create(
            account=conversation.account,
            contact=conversation.contact,
            conversation=conversation,
            direction='outbound',
            message_type='text',
            content=mensagem_completa,
            timestamp=timezone.now(),
            status='sending',  # Status inicial
            sent_by=request.user
        )
        
        # 2. Tenta enviar via WhatsApp API
        try:
            from core.services.whatsapp_api import WhatsAppAPIService
            
            api = WhatsAppAPIService(conversation.account)
            
            # Remove + do número se existir (API espera sem +)
            to_number = conversation.contact.phone_number.lstrip('+')
            
            # Envia mensagem
            api_response = api.send_text_message(
                to=to_number,
                message=mensagem_completa
            )
            
            # 3. Se API retornou sucesso, atualiza status e wamid
            if api_response.get('messages') and len(api_response['messages']) > 0:
                api_message = api_response['messages'][0]
                message.status = 'sent'
                message.wamid = api_message.get('id', f'local_{timezone.now().timestamp()}')
                message.save(update_fields=['status', 'wamid'])
                
                logger.info(f"Mensagem enviada via API - WAMID: {message.wamid}")
            else:
                raise Exception("API não retornou ID da mensagem")
                
        except Exception as api_error:
            # Se falhar no envio da API, atualiza status para 'failed'
            message.status = 'failed'
            message.error_message = str(api_error)
            message.save(update_fields=['status', 'error_message'])
            
            logger.error(f"Erro ao enviar mensagem via API: {api_error}")
            
            return JsonResponse({
                'success': False, 
                'error': 'Erro ao enviar mensagem via WhatsApp',
                'message_id': message.id
            })
        
        # 4. Atualiza última atividade da conversa
        conversation.last_activity = timezone.now()
        if conversation.status == 'pending':
            conversation.status = 'in_progress'
        conversation.save(update_fields=['last_activity', 'status'])
        
        return JsonResponse({
            'success': True, 
            'message_id': message.id,
            'wamid': message.wamid,
            'status': message.status
        })
        
    except Exception as e:
        logger.error(f"Erro geral ao processar envio de mensagem: {e}")
        return JsonResponse({
            'success': False, 
            'error': 'Erro interno do servidor'
        })


# @login_required
# @user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
# @require_POST
# def finish_conversation(request, conversation_id):
#     """
#     Finaliza uma conversa - REMOVIDO: conclusão será feita em outro módulo
#     """
#     conversation = get_object_or_404(
#         WhatsAppConversation,
#         id=conversation_id,
#         assigned_to=request.user
#     )
#     
#     conversation.status = 'resolved'
#     conversation.resolved_at = timezone.now()
#     conversation.save()
#     
#     return JsonResponse({'success': True})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def resend_message(request, message_id):
    """
    Reenvia uma mensagem que falhou
    """
    from django.db import transaction
    
    # Busca a mensagem - aceita status 'failed' ou 'sending' (para casos de erro anterior)
    try:
        message = WhatsAppMessage.objects.get(
            id=message_id,
            sent_by=request.user,
            status__in=['failed', 'sending']
        )
    except WhatsAppMessage.DoesNotExist:
        # Se não encontrar, retorna as mensagens sem fazer nada
        conversation = WhatsAppConversation.objects.filter(
            messages__id=message_id
        ).first()
        if conversation:
            messages = conversation.messages.select_related('contact').order_by('timestamp')
            return render(request, 'comercial/whatsapp/partials/messages.html', {
                'messages': messages
            })
        return JsonResponse({'success': False, 'error': 'Mensagem não encontrada'})
    
    conversation = message.conversation
    
    try:
        from core.services.whatsapp_api import WhatsAppAPIService
        
        # Usa transação atômica para evitar problemas
        with transaction.atomic():
            # Atualiza status para 'sending'
            message.status = 'sending'
            message.error_message = ''
            message.save(update_fields=['status', 'error_message'])
        
        # Tenta reenviar via API (fora da transação)
        api = WhatsAppAPIService(conversation.account)
        to_number = conversation.contact.phone_number.lstrip('+')
        
        api_response = api.send_text_message(
            to=to_number,
            message=message.content
        )
        
        # Se sucesso, atualiza status
        if api_response.get('messages') and len(api_response['messages']) > 0:
            api_message = api_response['messages'][0]
            
            with transaction.atomic():
                message.status = 'sent'
                message.wamid = api_message.get('id', f'local_{timezone.now().timestamp()}')
                message.save(update_fields=['status', 'wamid'])
            
            logger.info(f"Mensagem reenviada com sucesso - WAMID: {message.wamid}")
        else:
            raise Exception("API não retornou ID da mensagem")
            
    except Exception as api_error:
        # Se falhar, volta para status 'failed'
        with transaction.atomic():
            # Recarrega a mensagem para evitar problemas de estado
            message.refresh_from_db()
            message.status = 'failed'
            message.error_message = str(api_error)[:500]  # Limita tamanho do erro
            message.save(update_fields=['status', 'error_message'])
        
        logger.error(f"Erro ao reenviar mensagem: {api_error}")
    
    # Retorna as mensagens atualizadas via HTMX
    messages = conversation.messages.select_related('contact').order_by('timestamp')
    return render(request, 'comercial/whatsapp/partials/messages.html', {
        'messages': messages
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def assign_conversation(request, conversation_id):
    """
    Atribui uma conversa ao usuário logado
    """
    conversation = get_object_or_404(WhatsAppConversation, id=conversation_id)
    
    if conversation.status != 'pending':
        return JsonResponse({'success': False, 'message': 'Esta conversa já foi atribuída ou não está disponível.'})
    
    # Atribui a conversa ao usuário
    conversation.assign_to_user(request.user)
    conversation.start_attendance()
    
    # Notifica via WebSocket sobre atribuição
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    if channel_layer:
        conversation_data = {
            'id': conversation.id,
            'contact_name': conversation.contact.display_name,
            'assigned_to': request.user.username,
            'status': conversation.status,
        }
        
        async_to_sync(channel_layer.group_send)(
            'whatsapp_comercial',
            {
                'type': 'conversation_assigned',
                'conversation': conversation_data
            }
        )
    
    return JsonResponse({'success': True, 'message': f'Conversa atribuída com sucesso!'})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def register_client(request):
    """
    Cadastra um cliente a partir do contato WhatsApp
    """
    try:
        from core.models import Pessoa, WhatsAppContact, Telefone, Email
        
        # Dados do formulário
        whatsapp_contact_id = request.POST.get('whatsapp_contact_id')
        nome = request.POST.get('nome', '').strip()
        tipo_doc = request.POST.get('tipo_doc', '').strip()
        doc = request.POST.get('doc', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Dados de telefone divididos
        ddi = request.POST.get('ddi', '').strip()
        ddd = request.POST.get('ddd', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        
        # Campos opcionais de endereço
        cep = request.POST.get('cep', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        numero = request.POST.get('numero', '').strip()
        complemento = request.POST.get('complemento', '').strip()
        bairro = request.POST.get('bairro', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        pais = request.POST.get('pais', '').strip()
        
        # Validações básicas
        if not all([whatsapp_contact_id, nome, tipo_doc, doc, email, ddi, ddd, telefone]):
            return JsonResponse({
                'success': False, 
                'error': 'Todos os campos obrigatórios devem ser preenchidos'
            })
        
        # Verifica se o contato WhatsApp existe e pertence a uma conversa do usuário
        try:
            whatsapp_contact = WhatsAppContact.objects.get(
                id=whatsapp_contact_id,
                conversations__assigned_to=request.user
            )
        except WhatsAppContact.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Contato WhatsApp não encontrado'
            })
        
        # Verifica se já existe pessoa com este documento
        if Pessoa.objects.filter(doc=doc).exists():
            return JsonResponse({
                'success': False, 
                'error': f'Já existe um cliente cadastrado com este {tipo_doc.upper()}'
            })
        
        # Cria a pessoa
        pessoa = Pessoa.objects.create(
            nome=nome,
            tipo_doc=tipo_doc,
            doc=doc,
            endereco=endereco or None,
            numero=numero or None,
            complemento=complemento or None,
            bairro=bairro or None,
            cidade=cidade or None,
            estado=estado or None,
            pais=pais or None,
            cep=cep or None,
        )
        
        # Cria o telefone principal
        Telefone.objects.create(
            pessoa=pessoa,
            ddi=ddi,
            ddd=ddd,
            telefone=telefone,
            tipo='whatsapp',  # Marca como WhatsApp já que veio do WhatsApp
            principal=True
        )
        
        # Cria o email principal
        Email.objects.create(
            pessoa=pessoa,
            email=email,
            tipo='pessoal',
            principal=True
        )
        
        # Vincula o contato WhatsApp à pessoa criada
        whatsapp_contact.pessoa = pessoa
        whatsapp_contact.save()
        
        logger.info(f"Cliente {pessoa.nome} cadastrado e vinculado ao contato WhatsApp {whatsapp_contact.id}")
        
        return JsonResponse({
            'success': True,
            'pessoa_id': pessoa.id,
            'message': f'Cliente {pessoa.nome} cadastrado com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao cadastrar cliente: {e}")
        return JsonResponse({
            'success': False, 
            'error': 'Erro interno do servidor'
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
# def conversation_detail(request, conversation_id):
#     """
#     REMOVIDO - usar dashboard com ?conversation=ID
#     """
#     pass


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def mobile_conversation(request, conversation_id):
    """
    Retorna template do offcanvas mobile para uma conversa específica
    """
    conversation = get_object_or_404(
        WhatsAppConversation.objects.select_related('contact', 'account', 'contact__pessoa'),
        id=conversation_id
    )
    
    # Verifica se o usuário tem acesso a esta conversa
    if conversation.assigned_to != request.user:
        return HttpResponseForbidden("Você não tem acesso a esta conversa.")
    
    context = {
        'conversation': conversation,
    }
    
    return render(request, 'comercial/whatsapp/partials/mobile_conversation.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def media_modal(request):
    """
    Modal HTMX para visualizar mídia
    """
    media_url = request.GET.get('url')
    media_type = request.GET.get('type', 'image')
    media_name = request.GET.get('name', 'Mídia')
    
    context = {
        'media_url': media_url,
        'media_type': media_type,
        'media_name': media_name,
    }
    
    return render(request, 'comercial/whatsapp/partials/media_modal.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def send_message_form(request):
    """
    Envia mensagem WhatsApp via form data (para HTMX)
    Retorna apenas o HTML da nova mensagem enviada
    """
    conversation_id = request.POST.get('conversation_id')
    message_text = request.POST.get('message')
    
    if not message_text or not message_text.strip():
        return JsonResponse({'success': False, 'error': 'Mensagem não pode estar vazia'})
    
    conversation = get_object_or_404(
        WhatsAppConversation,
        id=conversation_id,
        assigned_to=request.user
    )
    
    try:
        # Cria mensagem local primeiro
        message = WhatsAppMessage.objects.create(
            conversation=conversation,
            direction='outbound',
            content=message_text.strip(),
            status='sending',
            sent_by=request.user
        )
        
        # Para fins de demonstração, marca como enviada
        # Em produção, aqui seria feita a chamada para API do WhatsApp
        message.status = 'sent'
        message.save()
        
        logger.info(f"Mensagem {message.id} enviada via mobile para conversa {conversation_id}")
        
        # Retorna HTML da mensagem para inserir no chat
        context = {
            'message': message,
            'show_sender': False,  # Mobile não mostra sender
        }
        
        return render(request, 'comercial/whatsapp/partials/message_item.html', context)
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem via mobile: {e}")
        return JsonResponse({'success': False, 'error': 'Erro ao enviar mensagem'})


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def mobile_conversation_content(request, conversation_id):
    """
    Retorna apenas o conteúdo da conversa mobile (sem header do offcanvas)
    """
    conversation = get_object_or_404(
        WhatsAppConversation.objects.select_related('contact', 'account', 'contact__pessoa'),
        id=conversation_id
    )
    
    # Verifica se o usuário tem acesso a esta conversa
    if conversation.assigned_to != request.user:
        return HttpResponseForbidden("Você não tem acesso a esta conversa.")
    
    context = {
        'conversation': conversation,
    }
    
    return render(request, 'comercial/whatsapp/partials/mobile_conversation_content.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def save_data_retorno(request):
    """
    Salva a data de retorno para uma conversa
    """
    conversation_id = request.POST.get('conversation_id')
    data_retorno = request.POST.get('data_retorno')
    
    if not conversation_id or not data_retorno:
        return render(request, 'comercial/whatsapp/partials/data_retorno_error.html', {
            'error': 'Dados incompletos.'
        })
    
    try:
        conversation = get_object_or_404(
            WhatsAppConversation,
            id=conversation_id,
            assigned_to=request.user
        )
        
        conversation.data_retorno = data_retorno
        conversation.save(update_fields=['data_retorno'])
        
        return render(request, 'comercial/whatsapp/partials/data_retorno_success.html')
        
    except Exception as e:
        logger.error(f"Erro ao salvar data de retorno: {e}")
        return render(request, 'comercial/whatsapp/partials/data_retorno_error.html', {
            'error': 'Erro ao salvar data de retorno.'
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def load_templates(request):
    """
    Carrega templates ativos para o select
    """
    templates = WhatsAppTemplate.objects.filter(
        status='approved',
        is_active=True
    ).order_by('name')
    
    return render(request, 'comercial/whatsapp/partials/template_options.html', {
        'templates': templates
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def preview_template(request):
    """
    Retorna preview do template com campos para parâmetros
    """
    template_id = request.GET.get('template_id')
    
    if not template_id:
        return render(request, 'comercial/whatsapp/preview_template.html', {
            'template': None
        })
    
    try:
        template = WhatsAppTemplate.objects.get(id=template_id)
        
        # Adiciona método helper para range de parâmetros
        import re
        param_count = len(re.findall(r'\{\{(\d+)\}\}', template.body_text or ''))
        template.get_parameter_count = lambda: param_count
        template.get_parameter_range = lambda: range(1, param_count + 1)
        
        return render(request, 'comercial/whatsapp/preview_template.html', {
            'template': template
        })
    except WhatsAppTemplate.DoesNotExist:
        return render(request, 'comercial/whatsapp/preview_template.html', {
            'template': None
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def template_preview(request):
    """
    Retorna preview do template e campos de parâmetros via HTMX
    """
    template_id = request.GET.get('template_id') or request.POST.get('template_id')
    
    if not template_id:
        return render(request, 'comercial/whatsapp/partials/template_preview.html', {
            'template': None,
            'param_count': 0
        })
    
    try:
        template = WhatsAppTemplate.objects.get(
            id=template_id,
            status='approved',
            is_active=True
        )
        
        # Conta parâmetros no template
        import re
        param_count = len(re.findall(r'\{\{(\d+)\}\}', template.body_text or ''))
        
        return render(request, 'comercial/whatsapp/partials/template_preview.html', {
            'template': template,
            'param_count': param_count,
            'param_range': list(range(1, param_count + 1))
        })
        
    except WhatsAppTemplate.DoesNotExist:
        return render(request, 'comercial/whatsapp/partials/template_preview.html', {
            'template': None,
            'param_count': 0
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def novo_contato(request):
    """
    Cria novo contato e inicia conversa WhatsApp
    """
    if request.method == 'POST':
        form = NovoContatoForm(request.POST)
        
        if not form.is_valid():
            
            # Retorna formulário com erros - mesmos dados do GET
            templates = WhatsAppTemplate.objects.filter(
                status='approved',
                is_active=True
            ).select_related('account').order_by('account__name', 'name')
            
            # Adiciona helper de parâmetros para cada template
            import re
            for template in templates:
                param_count = len(re.findall(r'\{\{(\d+)\}\}', template.body_text or ''))
                template.get_parameter_count = param_count
                template.get_parameter_range = list(range(1, param_count + 1))
            
            return render(request, 'comercial/whatsapp/partials/novo_contato_form_content.html', {
                'form': form,
                'templates': templates
            })
        
        phone_number = form.get_phone_number()
        template = form.cleaned_data['template_id']
        account = template.account
        nome = form.cleaned_data['nome']
        template_params = form.get_template_params()
        
        # Monta conteúdo do template com parâmetros
        body_text = template.body_text
        for param_num, param_value in template_params.items():
            body_text = body_text.replace(f'{{{{{param_num}}}}}', param_value)
        
        try:
            # Envia mensagem via API do WhatsApp primeiro
            from core.services.whatsapp_api import WhatsAppAPIService
            api_service = WhatsAppAPIService(account)
            
            # Monta componentes do template para a API
            components = []
            if template_params:
                body_params = []
                for param_num in sorted(template_params.keys()):
                    body_params.append({
                        "type": "text",
                        "text": template_params[param_num]
                    })
                
                components.append({
                    "type": "body",
                    "parameters": body_params
                })
            
            # Envia template via API
            response = api_service.send_template_message(
                phone_number,
                template.name,
                template.language,
                components
            )
            
            if response.get('success'):
                # Sucesso na API - agora cria contato, conversa e mensagem
                wamid = response.get('message_id', f"local_{timezone.now().timestamp()}")
                
                # Cria ou busca o contato
                contact, created = WhatsAppContact.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={
                        'name': nome,
                        'profile_name': nome,
                        'account': account,
                    }
                )
                
                if not created and not contact.name:
                    contact.name = nome
                    contact.save()
                
                # Cria nova conversa
                now = timezone.now()
                conversation = WhatsAppConversation.objects.create(
                    account=account,
                    contact=contact,
                    status='assigned',
                    assigned_to=request.user,
                    last_activity=now,
                    first_message_at=now,
                    assigned_at=now
                )
                
                # Cria mensagem no banco com WAMID real
                message = WhatsAppMessage.objects.create(
                    account=account,
                    contact=contact,
                    conversation=conversation,
                    direction='outbound',
                    message_type='template',
                    content=body_text,
                    timestamp=timezone.now(),
                    status='sent',
                    sent_by=request.user,
                    wamid=wamid
                )
                
                # Em caso de sucesso, retorna form limpo e trigger para fechar modal
                form = NovoContatoForm()  # Form limpo
                
                templates = WhatsAppTemplate.objects.filter(
                    status='approved',
                    is_active=True
                ).select_related('account').order_by('account__name', 'name')
                
                response = render(request, 'comercial/whatsapp/partials/novo_contato_form_content.html', {
                    'form': form,
                    'templates': templates,
                    'success': True
                })
                
                # Trigger para indicar sucesso
                import json
                response['HX-Trigger'] = json.dumps({
                    'closeModal': None,
                    'refreshConversations': None
                })
                
                return response
                
            else:
                # Erro no envio - adiciona erro ao form
                error_msg = response.get('error', 'Erro desconhecido ao enviar template')
                
                templates = WhatsAppTemplate.objects.filter(
                    status='approved',
                    is_active=True
                ).select_related('account').order_by('account__name', 'name')
                
                return render(request, 'comercial/whatsapp/partials/novo_contato_form_content.html', {
                    'form': form,
                    'templates': templates,
                    'api_error': f'Erro ao enviar template: {error_msg}'
                })
                
        except Exception as api_error:
            logger.error(f"Erro na API WhatsApp: {api_error}")
            
            templates = WhatsAppTemplate.objects.filter(
                status='approved',
                is_active=True
            ).select_related('account').order_by('account__name', 'name')
            
            return render(request, 'comercial/whatsapp/partials/novo_contato_form_content.html', {
                'form': form,
                'templates': templates,
                'api_error': f'Erro de conexão com WhatsApp: {str(api_error)}'
            })
            
        except Exception as e:
            # Com ATOMIC_REQUESTS=True, não podemos fazer queries após exceção
            # Retorna erro HTML simples sem renderizar template
            from django.http import HttpResponse
            html = f'''
            <div class="alert alert-danger">
                <h6 class="alert-heading">Erro ao criar contato</h6>
                <p class="mb-0">Erro ao criar contato: {str(e)}</p>
                <hr>
                <button class="btn btn-sm btn-outline-danger" onclick="location.reload()">
                    <i class="fas fa-redo me-1"></i> Tentar Novamente
                </button>
            </div>
            '''
            return HttpResponse(html)
    
    # GET - retorna modal com form
    form = NovoContatoForm()
    
    templates = WhatsAppTemplate.objects.filter(
        status='approved',
        is_active=True
    ).order_by('name')
    
    # Adiciona helper de parâmetros para cada template
    import re
    for template in templates:
        param_count = len(re.findall(r'\{\{(\d+)\}\}', template.body_text or ''))
        template.get_parameter_count = param_count
        template.get_parameter_range = list(range(1, param_count + 1))
    
    return render(request, 'comercial/whatsapp/modal_novo_contato.html', {
        'form': form,
        'templates': templates
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def send_template(request):
    """
    Envia template para a conversa
    """
    conversation_id = request.POST.get('conversation_id')
    template_id = request.POST.get('template_id')
    
    # Debug logs para rastrear problema
    logger.info(f"🔧 send_template chamado:")
    logger.info(f"  - conversation_id: '{conversation_id}' (tipo: {type(conversation_id)})")
    logger.info(f"  - template_id: '{template_id}' (tipo: {type(template_id)})")
    logger.info(f"  - POST data: {dict(request.POST)}")
    
    if not conversation_id or not template_id:
        logger.warning(f"❌ Dados incompletos - conversation_id: '{conversation_id}', template_id: '{template_id}'")
        return render(request, 'comercial/whatsapp/partials/send_template_error.html', {
            'error': 'Dados incompletos.'
        })
    
    try:
        conversation = get_object_or_404(
            WhatsAppConversation,
            id=conversation_id,
            assigned_to=request.user
        )
        
        template = get_object_or_404(
            WhatsAppTemplate,
            id=template_id,
            status='approved',
            is_active=True
        )
        
        # Processa o conteúdo do template
        template_content = []
        
        # Adiciona cabeçalho se existir
        if template.header_text:
            template_content.append(f"*{template.header_text}*")
        
        # Adiciona corpo da mensagem (obrigatório)
        body_text = template.body_text
        
        # Substitui variáveis por valores de exemplo ({{1}}, {{2}}, etc.)
        # Em produção, isso deveria vir de um formulário ou dados do cliente
        import re
        variables = re.findall(r'\{\{(\d+)\}\}', body_text)
        for var in set(variables):
            # Por enquanto, substitui por valores genéricos
            # Futuramente pode ser melhorado para coletar valores do usuário
            if var == '1':
                body_text = body_text.replace(f'{{{{{var}}}}}', conversation.contact.display_name or 'Cliente')
            elif var == '2':
                body_text = body_text.replace(f'{{{{{var}}}}}', 'Grupo ROM')
            else:
                body_text = body_text.replace(f'{{{{{var}}}}}', f'[Variável {var}]')
        
        template_content.append(body_text)
        
        # Adiciona rodapé se existir
        if template.footer_text:
            template_content.append(f"_{template.footer_text}_")
        
        # Adiciona prefixo com área de acesso e nome do usuário
        area_nome = "COMERCIAL"  # Área comercial
        usuario_nome = request.user.pessoa.nome if hasattr(request.user, 'pessoa') and request.user.pessoa else request.user.username
        prefixo = f"[{area_nome}] - {usuario_nome}\n"
        
        # Junta tudo com quebras de linha
        final_content = prefixo + '\n\n'.join(template_content)
        
        # Envia template via WhatsApp API
        from django.db import transaction
        from core.services.whatsapp_api import WhatsAppAPIService
        
        try:
            with transaction.atomic():
                # 1. Tenta enviar via WhatsApp API primeiro
                api = WhatsAppAPIService(conversation.account)
                to_number = conversation.contact.phone_number.lstrip('+')
                
                # Prepara componentes do template
                components = []
                if variables:
                    parameters = []
                    for var in sorted(set(variables), key=int):
                        if var == '1':
                            parameters.append({'type': 'text', 'text': conversation.contact.display_name or 'Cliente'})
                        elif var == '2':
                            parameters.append({'type': 'text', 'text': 'Grupo ROM'})
                        else:
                            parameters.append({'type': 'text', 'text': f'Variável {var}'})
                    
                    components = [{
                        'type': 'body',
                        'parameters': parameters
                    }]
                
                # Envia via WhatsApp API
                api_response = api.send_template_message(
                    to=to_number,
                    template_name=template.name,
                    language_code=template.language,
                    components=components if components else None
                )
                
                # Se falhar como template, tenta como texto
                if not api_response.get('success', False):
                    logger.warning(f"Template falhou, tentando como texto: {api_response.get('error')}")
                    text_response = api.send_text_message(to=to_number, message=final_content)
                    if text_response.get('success'):
                        api_response = text_response
                
                # Verifica se API retornou sucesso
                if not api_response.get('success', False):
                    raise Exception(f"Falha ao enviar mensagem: {api_response.get('error', 'Erro desconhecido')}")
                
                # Obtém message_id
                message_id = api_response.get('message_id')
                if not message_id:
                    raise Exception("API não retornou message_id")
                
                # 2. Só salva no banco se WhatsApp foi bem-sucedido
                message = WhatsAppMessage.objects.create(
                    account=conversation.account,
                    contact=conversation.contact,
                    conversation=conversation,
                    direction='outbound',
                    message_type='template',
                    content=final_content,
                    timestamp=timezone.now(),
                    status='sent',
                    wamid=message_id,
                    sent_by=request.user
                )
                
                # Atualiza conversa
                conversation.last_activity = timezone.now()
                if conversation.status == 'pending':
                    conversation.status = 'in_progress'
                conversation.save(update_fields=['last_activity', 'status'])
                
                logger.info(f"Template {template.display_name} enviado com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao enviar template: {e}")
            return render(request, 'comercial/whatsapp/partials/send_template_error_simple.html', {
                'error': 'Não foi possível enviar o template. Tente novamente.'
            })
        
        logger.info(f"Template {template.display_name} enviado para conversa {conversation_id}")
        
        # Retorna sucesso com atualização das mensagens
        return render(request, 'comercial/whatsapp/partials/send_template_success_simple.html', {
            'template': template,
            'message': message,
            'conversation': conversation
        })
        
    except Exception as e:
        logger.error(f"Erro ao enviar template: {e}")
        return render(request, 'comercial/whatsapp/partials/send_template_error_simple.html', {
            'error': 'Erro ao enviar template.'
        })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
@require_POST
def send_document(request):
    """
    Envia documento PDF via WhatsApp (HTMX)
    """
    import os
    from django.core.files.storage import default_storage
    from core.services.whatsapp_api import WhatsAppAPIService
    
    conversation_id = request.POST.get('conversation_id')
    if not conversation_id:
        return render(request, 'comercial/whatsapp/partials/send_document_error.html', {
            'error': 'ID da conversa não informado'
        })
    
    try:
        conversation = get_object_or_404(
            WhatsAppConversation.objects.select_related('account', 'contact'),
            id=conversation_id,
            assigned_to=request.user
        )
    except:
        return render(request, 'comercial/whatsapp/partials/send_document_error.html', {
            'error': 'Conversa não encontrada'
        })
    
    form = SendDocumentForm(request.POST, request.FILES)
    
    if not form.is_valid():
        return render(request, 'comercial/whatsapp/partials/send_document_form.html', {
            'form': form,
            'conversation': conversation
        })
    
    document = form.cleaned_data['document']
    caption = form.cleaned_data.get('caption', '').strip()
    
    try:
        # Gera nome único para o arquivo
        import uuid
        
        file_extension = '.pdf'
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # Organiza em estrutura hierárquica: media/whatsapp/documents/ano/mes/dia/
        now = timezone.now()
        folder_path = f"media/whatsapp/documents/{now.year}/{now.month:02d}/{now.day:02d}/"
        file_path = f"{folder_path}{filename}"
        
        # Salva no S3 (ou storage configurado)
        saved_path = default_storage.save(file_path, document)
        file_url = default_storage.url(saved_path)
        
        logger.info(f"Documento salvo: {saved_path} -> {file_url}")
        
        # Cria mensagem no banco
        message = WhatsAppMessage.objects.create(
            wamid=f"doc_{uuid.uuid4().hex[:16]}",  # Temporário até API responder
            account=conversation.account,
            contact=conversation.contact,
            conversation=conversation,
            direction='outbound',
            message_type='document',
            content=caption or f"Documento: {document.name}",
            media_url=file_url,
            media_filename=document.name,
            media_mimetype='application/pdf',
            status='sending',
            timestamp=timezone.now(),
            sent_by=request.user,
        )
        
        # Envia via API do WhatsApp
        api_service = WhatsAppAPIService(conversation.account)
        
        if settings.DEBUG:
            # Modo de desenvolvimento - simula sucesso
            logger.info(f"MOCK: Documento enviado - {document.name}")
            message.wamid = f"wamid_doc_{uuid.uuid4().hex}"
            message.status = 'sent'
            message.save()
        else:
            # Modo produção - envia real via API
            try:
                # Limpa o número do telefone (remove caracteres não numéricos)
                phone_number = ''.join(filter(str.isdigit, conversation.contact.phone_number))
                
                # Envia documento via API usando send_media_message
                api_response = api_service.send_media_message(
                    to=phone_number,
                    media_type='document',
                    media_url=file_url,
                    caption=caption or None,
                    filename=document.name  # IMPORTANTE: WhatsApp requer filename para documents
                )
                
                if api_response.get('success'):
                    # Sucesso na API - atualiza mensagem
                    message.wamid = api_response['message_id']
                    message.status = 'sent'
                    message.save()
                    logger.info(f"Documento enviado via API: {document.name} -> {phone_number}")
                else:
                    # Falha na API
                    error_msg = api_response.get('error', 'Erro desconhecido na API')
                    message.status = 'failed'
                    message.error_message = error_msg
                    message.save()
                    
                    logger.error(f"Falha na API WhatsApp: {error_msg}")
                    return render(request, 'comercial/whatsapp/partials/send_document_error.html', {
                        'error': f'Erro ao enviar documento: {error_msg}'
                    })
                
            except Exception as api_error:
                logger.error(f"Erro na API WhatsApp: {api_error}")
                message.status = 'failed'
                message.error_message = str(api_error)
                message.save()
                
                return render(request, 'comercial/whatsapp/partials/send_document_error.html', {
                    'error': f'Erro ao enviar documento: {api_error}'
                })
        
        logger.info(f"Documento PDF enviado: {document.name} para conversa {conversation_id}")
        
        # Retorna sucesso e atualiza área de mensagens
        return render(request, 'comercial/whatsapp/partials/send_document_success.html', {
            'message': message,
            'conversation': conversation,
            'document_name': document.name,
            'file_size': document.size
        })
        
    except Exception as e:
        logger.error(f"Erro ao enviar documento: {e}")
        # Remove arquivo do storage se houver erro
        try:
            if 'saved_path' in locals():
                default_storage.delete(saved_path)
        except:
            pass
        
        return render(request, 'comercial/whatsapp/partials/send_document_error.html', {
            'error': f'Erro interno ao enviar documento: {str(e)}'
        })