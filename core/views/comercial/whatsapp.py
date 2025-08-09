# -*- coding: utf-8 -*-
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from core.models import (
    WhatsAppAccount, WhatsAppTemplate, WhatsAppConversation, 
    WhatsAppMessage, WhatsAppContact
)

logger = logging.getLogger(__name__)


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
    
    return render(request, 'comercial/whatsapp/partials/messages.html', {
        'messages': messages
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
        # 1. Salva mensagem no banco primeiro com status 'sending'
        message = WhatsAppMessage.objects.create(
            account=conversation.account,
            contact=conversation.contact,
            conversation=conversation,
            direction='outbound',
            message_type='text',
            content=message_text.strip(),
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
                message=message_text.strip()
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
def conversation_detail(request, conversation_id):
    """
    Página de conversa individual para atendimento
    """
    conversation = get_object_or_404(
        WhatsAppConversation.objects.select_related('contact', 'account'),
        id=conversation_id
    )
    
    # Verifica se o usuário tem acesso a esta conversa
    if conversation.assigned_to != request.user:
        return JsonResponse({'success': False, 'message': 'Você não tem acesso a esta conversa.'})
    
    # Busca todas as mensagens da conversa
    messages_list = conversation.messages.select_related('sent_by').order_by('timestamp')
    
    # Marca mensagens como lidas
    unread_messages = messages_list.filter(
        direction='inbound',
        status__in=['sent', 'delivered']
    )
    for msg in unread_messages:
        msg.mark_as_read()
    
    context = {
        'title': f'Conversa - {conversation.contact.display_name}',
        'conversation': conversation,
        'messages': messages_list,
    }
    
    return render(request, 'comercial/whatsapp/conversation.html', context)