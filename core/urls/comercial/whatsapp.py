from django.urls import path
from core.views.comercial import whatsapp as views

urlpatterns = [
    path('', views.dashboard, name='whatsapp'),
    path('geral/', views.whatsapp_geral, name='whatsapp_geral'),
    
    # AJAX/HTMX endpoints
    path('my-conversations/', views.my_conversations, name='my_conversations'),
    path('pending-conversations/', views.pending_conversations, name='pending_conversations'),
    path('conversation/<int:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    path('conversation/<int:conversation_id>/messages-readonly/', views.conversation_messages_readonly, name='conversation_messages_readonly'),
    path('conversation/<int:conversation_id>/chat-area/', views.conversation_chat_area, name='conversation_chat_area'),
    path('mobile-conversation/<int:conversation_id>/', views.mobile_conversation, name='mobile_conversation'),
    path('mobile-conversation-content/<int:conversation_id>/', views.mobile_conversation_content, name='mobile_conversation_content'),
    path('pending-count/', views.pending_count, name='pending_count'),
    path('media-modal/', views.media_modal, name='media_modal'),
    
    # Actions
    path('assign/<int:conversation_id>/', views.assign_conversation, name='assign_conversation'),
    path('check-24h-window/', views.check_24h_window, name='check_24h_window'),
    path('send-message/', views.send_message, name='send_message'),
    path('send-message-form/', views.send_message_form, name='send_message_form'),
    path('resend-message/<int:message_id>/', views.resend_message, name='resend_message'),
    path('register-client/', views.register_client, name='register_client'),
    path('save-data-retorno/', views.save_data_retorno, name='save_data_retorno'),
    path('load-templates/', views.load_templates, name='load_templates'),
    path('preview-template/', views.preview_template, name='whatsapp_preview_template'),
    path('template-preview/', views.template_preview, name='template_preview'),
    path('send-template/', views.send_template, name='send_template'),
    path('novo-contato/', views.novo_contato, name='whatsapp_novo_contato'),
    
    # Debug
    path('test-websocket/', views.test_websocket, name='test_websocket'),
    # path('finish/<int:conversation_id>/', views.finish_conversation, name='finish_conversation'),  # Removido - conclusão em outro módulo
    
    # Removido: conversation_detail - usar dashboard com ?conversation=ID
    path('conversations-table/', views.conversations_table, name='conversations_table'),
]