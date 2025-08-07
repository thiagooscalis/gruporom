from django.urls import path
from core.views.base import redirect_to_group

urlpatterns = [
    path('', redirect_to_group, name='redirect_to_group'),
]