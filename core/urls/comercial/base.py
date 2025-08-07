from django.urls import path, include
from core.views.comercial.base import home

urlpatterns = [
    path('', home, name='home'),
    path('whatsapp/', include('core.urls.comercial.whatsapp')),
]