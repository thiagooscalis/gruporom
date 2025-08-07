from django.urls import path, include

app_name = 'comercial'

urlpatterns = [
    path('', include('core.urls.comercial.base')),
]