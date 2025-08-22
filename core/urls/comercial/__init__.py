from django.urls import path, include

app_name = 'comercial'

urlpatterns = [
    path('', include('core.urls.comercial.base')),
    path('nova-venda/', include('core.urls.comercial.pre_venda')),
]