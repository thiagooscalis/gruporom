# -*- coding: utf-8 -*-
from core.models import WhatsAppAccount, WhatsAppContact, WhatsAppMessage, Usuario
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def seed_whatsapp():
    """
    Cria dados de teste para WhatsApp
    """
    logger.info("Criando dados de teste para WhatsApp...")
    
    # Busca usuário admin
    try:
        admin_user = Usuario.objects.get(username='thiago')
    except Usuario.DoesNotExist:
        logger.error("Usuário admin 'thiago' não encontrado. Execute o seed de usuários primeiro.")
        return
    
    # Cria conta WhatsApp de teste
    account, created = WhatsAppAccount.objects.get_or_create(
        phone_number_id='123456789012345',
        defaults={
            'name': 'Grupo ROM - Teste',
            'phone_number': '+5511999999999',
            'access_token': 'TESTE_ACCESS_TOKEN_AQUI',
            'webhook_verify_token': 'TESTE_WEBHOOK_TOKEN_123',
            'business_account_id': '987654321098765',
            'status': 'active',
            'is_active': True,
            'responsavel': admin_user,
        }
    )
    
    if created:
        logger.info(f"Conta WhatsApp criada: {account.name}")
    else:
        logger.info(f"Conta WhatsApp já existe: {account.name}")
    
    # Cria contatos de teste
    contatos_teste = [
        {
            'phone_number': '+5511987654321',
            'name': 'Cliente Teste 1',
            'profile_name': 'João Silva',
            'is_business': False,
        },
        {
            'phone_number': '+5511876543210',
            'name': 'Fornecedor ABC',
            'profile_name': 'Empresa ABC Ltda',
            'is_business': True,
        },
        {
            'phone_number': '+5511765432109',
            'name': 'Maria Santos',
            'profile_name': 'Maria',
            'is_business': False,
        },
    ]
    
    for contato_data in contatos_teste:
        contact, created = WhatsAppContact.objects.get_or_create(
            account=account,
            phone_number=contato_data['phone_number'],
            defaults={
                'name': contato_data['name'],
                'profile_name': contato_data['profile_name'],
                'is_business': contato_data['is_business'],
                'last_seen': timezone.now() - timedelta(hours=2),
            }
        )
        
        if created:
            logger.info(f"Contato criado: {contact.name}")
            
            # Cria mensagens de teste para cada contato
            mensagens_teste = [
                {
                    'direction': 'inbound',
                    'message_type': 'text',
                    'content': f'Olá! Esta é uma mensagem de teste do {contact.name}',
                    'status': 'delivered',
                    'hours_ago': 5,
                },
                {
                    'direction': 'outbound',
                    'message_type': 'text',
                    'content': f'Olá {contact.name}! Obrigado pelo contato. Como podemos ajudar?',
                    'status': 'read',
                    'hours_ago': 4,
                    'sent_by': admin_user,
                },
                {
                    'direction': 'inbound',
                    'message_type': 'text',
                    'content': 'Gostaria de saber mais sobre os serviços da empresa.',
                    'status': 'delivered',
                    'hours_ago': 3,
                },
                {
                    'direction': 'outbound',
                    'message_type': 'text',
                    'content': 'Claro! Temos vários serviços disponíveis. Vou te enviar mais informações.',
                    'status': 'delivered',
                    'hours_ago': 2,
                    'sent_by': admin_user,
                },
            ]
            
            for i, msg_data in enumerate(mensagens_teste):
                timestamp = timezone.now() - timedelta(hours=msg_data['hours_ago'])
                
                message = WhatsAppMessage.objects.create(
                    wamid=f'wamid.{account.id}_{contact.id}_{i}_{int(timestamp.timestamp())}',
                    account=account,
                    contact=contact,
                    direction=msg_data['direction'],
                    message_type=msg_data['message_type'],
                    content=msg_data['content'],
                    status=msg_data['status'],
                    timestamp=timestamp,
                    sent_by=msg_data.get('sent_by'),
                )
                
                # Define delivered_at e read_at baseado no status
                if message.status in ['delivered', 'read']:
                    message.delivered_at = timestamp + timedelta(seconds=30)
                if message.status == 'read':
                    message.read_at = timestamp + timedelta(minutes=5)
                message.save()
        else:
            logger.info(f"Contato já existe: {contact.name}")
    
    logger.info("Dados de teste do WhatsApp criados com sucesso!")
    logger.info(f"Conta criada: {account.name} ({account.display_phone})")
    logger.info(f"Contatos: {WhatsAppContact.objects.filter(account=account).count()}")
    logger.info(f"Mensagens: {WhatsAppMessage.objects.filter(account=account).count()}")
    
    return account