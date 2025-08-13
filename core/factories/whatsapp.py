# -*- coding: utf-8 -*-
import factory
from factory.django import DjangoModelFactory
from core.models import WhatsAppAccount, WhatsAppTemplate, WhatsAppContact, WhatsAppConversation, WhatsAppMessage
from .usuario import UsuarioFactory


class WhatsAppAccountFactory(DjangoModelFactory):
    """Factory para criar contas WhatsApp"""
    
    class Meta:
        model = WhatsAppAccount
    
    name = factory.Sequence(lambda n: f"Conta WhatsApp {n}")
    phone_number = factory.Sequence(lambda n: f"+5511{9000000 + n}")
    phone_number_id = factory.Sequence(lambda n: f"{100000000 + n}")
    business_account_id = factory.Sequence(lambda n: f"{200000000 + n}")
    access_token = "test_token"
    responsavel = factory.SubFactory(UsuarioFactory)
    is_active = True


class WhatsAppTemplateFactory(DjangoModelFactory):
    """Factory para criar templates WhatsApp"""
    
    class Meta:
        model = WhatsAppTemplate
    
    account = factory.SubFactory(WhatsAppAccountFactory)
    name = factory.Sequence(lambda n: f"template_{n}")
    display_name = factory.Sequence(lambda n: f"Template {n}")
    body_text = "Olá {{1}}, bem-vindo ao {{2}}!"
    status = "approved"
    is_active = True
    language = "pt_BR"
    criado_por = factory.SubFactory(UsuarioFactory)


class WhatsAppTemplateSimpleFactory(DjangoModelFactory):
    """Factory para criar templates WhatsApp sem parâmetros"""
    
    class Meta:
        model = WhatsAppTemplate
    
    account = factory.SubFactory(WhatsAppAccountFactory)
    name = factory.Sequence(lambda n: f"template_simples_{n}")
    display_name = factory.Sequence(lambda n: f"Template Simples {n}")
    body_text = "Mensagem simples sem variáveis"
    status = "approved"
    is_active = True
    language = "pt_BR"
    criado_por = factory.SubFactory(UsuarioFactory)


class WhatsAppContactFactory(DjangoModelFactory):
    """Factory para criar contatos WhatsApp"""
    
    class Meta:
        model = WhatsAppContact
    
    account = factory.SubFactory(WhatsAppAccountFactory)
    phone_number = factory.Sequence(lambda n: f"+5511{9000000 + n}")
    name = factory.Faker('name', locale='pt_BR')
    profile_name = factory.SelfAttribute('name')


class WhatsAppConversationFactory(DjangoModelFactory):
    """Factory para criar conversas WhatsApp"""
    
    class Meta:
        model = WhatsAppConversation
    
    account = factory.SubFactory(WhatsAppAccountFactory)
    contact = factory.SubFactory(WhatsAppContactFactory)
    status = 'pending'
    assigned_to = factory.SubFactory(UsuarioFactory)
    first_message_at = factory.Faker('date_time_this_year')
    assigned_at = factory.Faker('date_time_this_year')
    last_activity = factory.Faker('date_time_this_year')


class WhatsAppMessageFactory(DjangoModelFactory):
    """Factory para criar mensagens WhatsApp"""
    
    class Meta:
        model = WhatsAppMessage
    
    account = factory.SubFactory(WhatsAppAccountFactory)
    contact = factory.SubFactory(WhatsAppContactFactory)
    conversation = factory.SubFactory(WhatsAppConversationFactory)
    wamid = factory.Sequence(lambda n: f"wamid.test_{n}")
    direction = 'inbound'
    message_type = 'text'
    content = factory.Faker('text', max_nb_chars=100, locale='pt_BR')
    timestamp = factory.Faker('date_time_this_year')
    status = 'delivered'