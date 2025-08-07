from django.urls import path
from core.views.base import redirect_to_group, privacidade_inclusive

urlpatterns = [
    path('', redirect_to_group, name='redirect_to_group'),
    path('inclusive/privacidade/', privacidade_inclusive, name='privacidade_inclusive'),
]