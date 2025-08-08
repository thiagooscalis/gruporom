from django.urls import path
from core.views.base import redirect_to_group, privacidade_inclusive, termos_inclusive, cadastrar_pessoa_view

urlpatterns = [
    path('', redirect_to_group, name='redirect_to_group'),
    path('inclusive/privacidade/', privacidade_inclusive, name='privacidade_inclusive'),
    path('inclusive/termos/', termos_inclusive, name='termos_inclusive'),
    path('pessoa/cadastrar/', cadastrar_pessoa_view, name='cadastrar_pessoa'),
]