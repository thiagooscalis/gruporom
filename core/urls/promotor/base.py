from django.urls import path

from core.views.promotor.base import home_view
from core.views.promotor.caravana import cadastrar_caravana_view

urlpatterns = [
    path("", home_view, name="home"),
    path("caravana/cadastrar/", cadastrar_caravana_view, name="cadastrar_caravana"),
]