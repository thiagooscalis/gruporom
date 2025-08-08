from django.urls import path, include

from .base import urlpatterns as base_patterns

app_name = "promotor"

urlpatterns = [
    path("", include(base_patterns)),
]