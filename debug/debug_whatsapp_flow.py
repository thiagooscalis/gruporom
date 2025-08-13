#!/usr/bin/env python
"""
Script para testar o fluxo completo do WhatsApp Comercial
Cria dados de teste para simular conversas chegando via webhook
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    WhatsAppAccount, WhatsAppContact, WhatsAppMessage, 
    WhatsAppConversation, Usuario
)
from django.utils import timezone

def create_test_data():
    """Cria dados de teste para WhatsApp"""
    print("🔧 Criando dados de teste para WhatsApp...")
    
    # Busca usuário admin
    try:
        admin_user = Usuario.objects.get(username='thiago')
        print(f"✅ Usuário admin encontrado: {admin_user.username}")
    except Usuario.DoesNotExist:
        print("❌ Usuário admin 'thiago' não encontrado!")
        return
    
    # Cria conta WhatsApp de teste (se não existir)
    account, created = WhatsAppAccount.objects.get_or_create(
        phone_number='+5511999999999',
        defaults={
            'name': 'Grupo ROM - Principal',
            'phone_number_id': 'test_123456789',
            'business_account_id': 'test_business_123',
            'access_token': 'test_token_12345',
            'webhook_verify_token': 'test_verify_token',
            'status': 'active',
            'is_active': True,
            'responsavel': admin_user,
        }
    )
    
    if created:
        print(f"✅ Conta WhatsApp criada: {account.name}")
    else:
        print(f"✅ Conta WhatsApp existente: {account.name}")
    
    # Lista de contatos para criar conversas (incluindo mídias)
    test_contacts = [
        {
            'phone': '+5511987654321',
            'name': 'João Silva',
            'messages': [
                'Olá! Gostaria de saber mais sobre os serviços da empresa.',
                'Estou interessado em fazer um orçamento.',
            ]
        },
        {
            'phone': '+5511876543210', 
            'name': 'Maria Santos',
            'messages': [
                'Boa tarde! Vi vocês no Google e queria tirar algumas dúvidas.',
                'Vocês trabalham com projetos personalizados?',
                'Qual seria o prazo de entrega?'
            ]
        },
        {
            'phone': '+5511765432109',
            'name': 'Pedro Costa',
            'messages': [
                'Olá, preciso de um orçamento urgente!',
                {'type': 'image', 'caption': 'Aqui está a foto do projeto que preciso'},
                {'type': 'document', 'filename': 'orcamento.pdf', 'caption': 'Orçamento que recebi de outro fornecedor'},
            ]
        },
        {
            'phone': '+5511654321098',
            'name': 'Ana Paula',
            'messages': [
                'Bom dia! Gostaria de agendar uma reunião.',
                {'type': 'audio', 'caption': ''},
                'Estou disponível esta semana.',
            ]
        },
        {
            'phone': '+5511543210987',
            'name': 'Carlos Oliveira',
            'messages': [
                'Oi! Quero mostrar o local onde seria o projeto.',
                {'type': 'video', 'caption': 'Vídeo do terreno onde seria a construção'},
                'Podem fazer uma visita técnica?'
            ]
        }
    ]
    
    print(f"📞 Criando {len(test_contacts)} contatos com conversas...")
    
    for contact_data in test_contacts:
        # Cria ou busca contato
        contact, created = WhatsAppContact.objects.get_or_create(
            account=account,
            phone_number=contact_data['phone'],
            defaults={
                'name': contact_data['name'],
                'profile_name': contact_data['name'],
            }
        )
        
        if created:
            print(f"  ✅ Contato criado: {contact.name} ({contact.phone_number})")
        else:
            print(f"  ✅ Contato existente: {contact.name}")
        
        # Verifica se já existe conversa ativa
        existing_conversation = WhatsAppConversation.objects.filter(
            account=account,
            contact=contact,
            status__in=['pending', 'assigned', 'in_progress']
        ).first()
        
        if existing_conversation:
            print(f"    ℹ️ Conversa já existe (Status: {existing_conversation.status})")
            continue
        
        # Cria nova conversa
        now = timezone.now()
        first_message_time = now - timedelta(minutes=len(contact_data['messages']) * 2)
        
        conversation = WhatsAppConversation.objects.create(
            account=account,
            contact=contact,
            status='pending',  # Aguardando atendimento
            first_message_at=first_message_time,
            priority='medium'
        )
        
        print(f"    ✅ Conversa criada (ID: {conversation.id}, Status: {conversation.status})")
        
        # Cria mensagens para esta conversa
        for i, message_data in enumerate(contact_data['messages']):
            message_time = first_message_time + timedelta(minutes=i * 2)
            wamid = f"test_msg_{account.id}_{contact.id}_{i}_{int(message_time.timestamp())}"
            
            # Verifica se é uma mensagem de texto ou mídia
            if isinstance(message_data, str):
                # Mensagem de texto
                message = WhatsAppMessage.objects.create(
                    wamid=wamid,
                    account=account,
                    contact=contact,
                    conversation=conversation,
                    direction='inbound',
                    message_type='text',
                    content=message_data,
                    timestamp=message_time,
                    status='delivered'
                )
                print(f"      📨 Mensagem texto: \"{message_data[:30]}...\"")
                
            elif isinstance(message_data, dict):
                # Mensagem de mídia
                media_type = message_data['type']
                caption = message_data.get('caption', '')
                filename = message_data.get('filename', f'arquivo_{media_type}')
                
                # URLs de teste para diferentes tipos de mídia
                test_media_urls = {
                    'image': 'https://via.placeholder.com/400x300/0066cc/ffffff.jpg?text=Projeto+Exemplo',
                    'video': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                    'audio': 'https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav', 
                    'document': 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
                }
                
                # Mimetypes para cada tipo
                mime_types = {
                    'image': 'image/jpeg',
                    'video': 'video/mp4', 
                    'audio': 'audio/wav',
                    'document': 'application/pdf'
                }
                
                message = WhatsAppMessage.objects.create(
                    wamid=wamid,
                    account=account,
                    contact=contact,
                    conversation=conversation,
                    direction='inbound',
                    message_type=media_type,
                    content=caption,
                    timestamp=message_time,
                    status='delivered',
                    media_id=f'test_{media_type}_{wamid}',
                    media_url=test_media_urls.get(media_type, ''),
                    media_filename=filename,
                    media_mimetype=mime_types.get(media_type, 'application/octet-stream')
                )
                
                emoji_map = {
                    'image': '📷',
                    'video': '🎥', 
                    'audio': '🎵',
                    'document': '📄'
                }
                
                emoji = emoji_map.get(media_type, '📎')
                display_name = caption if caption else filename
                print(f"      {emoji} Mensagem {media_type}: {display_name}")
        
        # Atualiza última atividade da conversa
        conversation.last_activity = now - timedelta(minutes=1)
        conversation.save(update_fields=['last_activity'])
    
    print("\n🎉 Dados de teste criados com sucesso!")
    print("\n📋 Resumo:")
    print(f"   - Contas WhatsApp: {WhatsAppAccount.objects.count()}")
    print(f"   - Contatos: {WhatsAppContact.objects.count()}")
    print(f"   - Conversas: {WhatsAppConversation.objects.count()}")
    print(f"   - Mensagens: {WhatsAppMessage.objects.count()}")
    
    # Mostra conversas pendentes
    pending_conversations = WhatsAppConversation.objects.filter(status='pending')
    print(f"\n⏳ Conversas aguardando atendimento: {pending_conversations.count()}")
    
    for conv in pending_conversations:
        print(f"   - {conv.contact.display_name}: {conv.messages.count()} mensagens")
    
    print(f"\n🔗 Acesse: http://localhost:8000/comercial/whatsapp/")
    print("   (Faça login com usuário 'thiago' e senha 'admin123')")

if __name__ == '__main__':
    create_test_data()