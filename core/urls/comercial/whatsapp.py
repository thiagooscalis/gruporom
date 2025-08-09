from django.urls import path
from core.views.comercial import whatsapp as views

urlpatterns = [
    path('', views.dashboard, name='whatsapp'),
    
    # AJAX/HTMX endpoints
    path('my-conversations/', views.my_conversations, name='my_conversations'),
    path('pending-conversations/', views.pending_conversations, name='pending_conversations'),
    path('conversation/<int:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    path('pending-count/', views.pending_count, name='pending_count'),
    
    # Actions
    path('assign/<int:conversation_id>/', views.assign_conversation, name='assign_conversation'),
    path('send-message/', views.send_message, name='send_message'),
    path('register-client/', views.register_client, name='register_client'),
    # path('finish/<int:conversation_id>/', views.finish_conversation, name='finish_conversation'),  # Removido - conclusão em outro módulo
    
    # Legacy
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations-table/', views.conversations_table, name='conversations_table'),
]