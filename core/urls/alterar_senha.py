from django.urls import path
from core.views.alterar_senha import alterar_senha_form, alterar_senha_submit

urlpatterns = [
    path('alterar-senha/form/', alterar_senha_form, name='alterar_senha_form'),
    path('alterar-senha/submit/', alterar_senha_submit, name='alterar_senha_submit'),
]