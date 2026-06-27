from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('apps.web.urls')),
    path('catalogo/', include('apps.catalogo.urls')),
    path('operacion/', include('apps.operacion.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
