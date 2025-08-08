# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from core.models import (
    WhatsAppAccount, WhatsAppTemplate, WhatsAppConversation, 
    WhatsAppMessage, WhatsAppContact
)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def dashboard(request):
    """
    Dashboard do WhatsApp comercial - Lista conversas aguardando atendimento
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
    
    # Estatísticas
    total_pending = pending_conversations.count()
    my_conversations = WhatsAppConversation.objects.filter(
        assigned_to=request.user,
        status__in=['assigned', 'in_progress']
    ).count()
    
    context = {
        'title': 'WhatsApp - Atendimento Comercial',
        'pending_conversations': pending_conversations,
        'total_pending': total_pending,
        'my_conversations': my_conversations,
    }
    
    return render(request, 'comercial/whatsapp/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comercial').exists())
def assign_conversation(request, conversation_id):
    """
    Atribui uma conversa ao usuário logado
    """
    conversation = get_object_or_404(WhatsAppConversation, id=conversation_id)
    
    if conversation.status != 'pending':
        messages.error(request, 'Esta conversa já foi atribuída ou não está disponível.')
        return redirect('comercial:whatsapp')
    
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
    
    messages.success(request, f'Conversa com {conversation.contact.display_name} atribuída a você.')
    return redirect('comercial:conversation_detail', conversation_id=conversation.id)


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
        messages.error(request, 'Você não tem acesso a esta conversa.')
        return redirect('comercial:whatsapp')
    
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