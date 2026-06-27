from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('artistas/', views.artistas, name='artistas'),
    path('albumes/', views.albumes, name='albumes'),
    path('suscripciones/', views.suscripciones, name='suscripciones'),
    path('suscripciones/contratar/<str:plan>/', views.contratar_plan, name='contratar'),
    path('contacto/', views.contacto, name='contacto'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
