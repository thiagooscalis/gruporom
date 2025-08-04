from django.urls import path
from core.views.administracao.base import home

urlpatterns = [
    path('', home, name='home'),
]