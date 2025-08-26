from django.urls import path, include
from core.views.comercial.base import home, nova_venda, caravanas_disponiveis, caravana_detalhes

urlpatterns = [
    path('', home, name='home'),
    path('nova-venda/', nova_venda, name='nova_venda'),
    path('nova-venda/caravanas/', caravanas_disponiveis, name='caravanas_disponiveis'),
    path('nova-venda/caravanas/<int:caravana_id>/', caravana_detalhes, name='caravana_detalhes'),
    path('pre-vendas/', include('core.urls.comercial.pre_vendas')),
    path('whatsapp/', include('core.urls.comercial.whatsapp')),
]