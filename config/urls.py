from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path("admin/", admin.site.urls),

    # ============================================================
    # API REST (sin prefijo de idioma)
    # ============================================================
    path("api/auth/", obtain_auth_token, name="api_token_auth"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("api.urls")),
]

# Rutas con prefijo de idioma (/es/, /en/, /ja/...)
urlpatterns += i18n_patterns(
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("estudiante/", include("gamificacion.urls")),
    path("certificados/", include("certificaciones.urls")),
    path("contenido/", include("contenido.urls")),
    path("profesor/", include("profesor.urls")),
    path('', include('academia.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)