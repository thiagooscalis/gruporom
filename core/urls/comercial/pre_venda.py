from django.urls import path
from core.views.comercial.pre_venda import nova_venda, caravanas_ativas, caravana_venda, bloqueio_modal

urlpatterns = [
    path('', nova_venda, name='nova_venda'),
    path('caravanas/', caravanas_ativas, name='caravanas_ativas'),
    path('caravanas/<int:pk>/', caravana_venda, name='caravana_venda'),
    path('bloqueio/<int:pk>/modal/', bloqueio_modal, name='bloqueio_modal'),
]