from django.urls import path
from core.views.operacional.base import home

urlpatterns = [
    path('', home, name='home'),
]