from django.urls import path
from core.views.comercial.pre_vendas import (
    pre_vendas_lista,
    iniciar_venda_caravana,
    pre_venda_detalhe,
)

urlpatterns = [
    path('', pre_vendas_lista, name='pre_vendas_lista'),
    path('<int:venda_id>/', pre_venda_detalhe, name='pre_venda_detalhe'),
    path('iniciar-venda-caravana/<int:caravana_id>/', iniciar_venda_caravana, name='iniciar_venda_caravana'),
]