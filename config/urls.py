from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import logout_then_login
from core.views.administracao.whatsapp import webhook

urlpatterns = [
    path("", include("core.urls.base")),
    path("logout/", logout_then_login, name="logout"),
    path("", include("django.contrib.auth.urls")),
    path("", include("core.urls.areas")),  # URLs globais com parâmetro area
    path("", include("core.urls.alterar_senha")),  # URLs para alterar senha
    # Webhook WhatsApp (fora de administração para não exigir login)
    path(
        "webhook/whatsapp/<int:account_id>/", webhook, name="whatsapp_webhook"
    ),
    path("administracao/", include("core.urls.administracao")),
    path("comercial/", include("core.urls.comercial")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
