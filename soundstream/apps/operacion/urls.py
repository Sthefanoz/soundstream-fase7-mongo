from django.urls import path
from . import views

app_name = 'operacion'

urlpatterns = [
    path('historial/', views.historial_usuario, name='historial'),
    path('regalias/', views.reporte_regalias, name='regalias'),
]
