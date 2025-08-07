from django.urls import path
from core.views.comercial.whatsapp import dashboard, assign_conversation, conversation_detail

urlpatterns = [
    path('', dashboard, name='whatsapp'),
    path('assign/<int:conversation_id>/', assign_conversation, name='assign_conversation'),
    path('conversation/<int:conversation_id>/', conversation_detail, name='conversation_detail'),
]