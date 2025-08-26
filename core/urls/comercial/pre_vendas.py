from django.urls import path
from core.views.comercial.pre_vendas import pre_vendas_lista

urlpatterns = [
    path('', pre_vendas_lista, name='pre_vendas_lista'),
]