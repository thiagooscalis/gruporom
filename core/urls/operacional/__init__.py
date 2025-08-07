from django.urls import path, include

app_name = 'operacional'

urlpatterns = [
    path('', include('core.urls.operacional.base')),
    path('caravanas/', include('core.urls.operacional.caravanas')),
]