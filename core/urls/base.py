from django.urls import path
from core.views.base import redirect_to_group, privacidade_inclusive, termos_inclusive

urlpatterns = [
    path('', redirect_to_group, name='redirect_to_group'),
    path('inclusive/privacidade/', privacidade_inclusive, name='privacidade_inclusive'),
    path('inclusive/termos/', termos_inclusive, name='termos_inclusive'),
]