from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    path('', include('core.urls.base')),
    path('logout/', logout_then_login, name='logout'),
    path('', include('django.contrib.auth.urls')),
    path('', include('core.urls.areas')),  # URLs globais com parâmetro area
    path('', include('core.urls.alterar_senha')),  # URLs para alterar senha
    path('administracao/', include('core.urls.administracao')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
