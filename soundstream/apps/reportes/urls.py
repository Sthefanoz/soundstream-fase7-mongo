from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.panel, name='panel'),
    path('top-canciones/', views.top_canciones, name='top_canciones'),
    path('top-artistas/', views.top_artistas, name='top_artistas'),
    path('regalias/', views.regalias_por_artista, name='regalias'),
    path('ingresos-por-plan/', views.ingresos_por_plan, name='ingresos_plan'),
    path('reproducciones-por-pais/', views.reproducciones_por_pais, name='repro_pais'),
    path('suscripciones/', views.suscripciones_resumen, name='suscripciones'),
]
