from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('artistas/<int:pk>/', views.detalle_artista, name='artista_detalle'),
    path('albumes/<int:pk>/', views.detalle_album, name='album_detalle'),
    path('canciones/<int:pk>/play/', views.reproducir_cancion, name='reproducir'),
    path('canciones/<int:pk>/preview/', views.preview_cancion, name='preview'),

    # Panel de administracion (CRUD del catalogo, solo admin)
    path('gestion/', views.gestion_panel, name='gestion_panel'),

    path('gestion/artistas/', views.gestion_artistas, name='gestion_artistas'),
    path('gestion/artistas/nuevo/', views.artista_form, name='artista_nuevo'),
    path('gestion/artistas/<int:pk>/editar/', views.artista_form, name='artista_editar'),
    path('gestion/artistas/<int:pk>/eliminar/', views.artista_eliminar, name='artista_eliminar'),

    path('gestion/albumes/', views.gestion_albumes, name='gestion_albumes'),
    path('gestion/albumes/nuevo/', views.album_form, name='album_nuevo'),
    path('gestion/albumes/<int:pk>/editar/', views.album_form, name='album_editar'),
    path('gestion/albumes/<int:pk>/eliminar/', views.album_eliminar, name='album_eliminar'),

    path('gestion/canciones/', views.gestion_canciones, name='gestion_canciones'),
    path('gestion/canciones/nuevo/', views.cancion_form, name='cancion_nuevo'),
    path('gestion/canciones/<int:pk>/editar/', views.cancion_form, name='cancion_editar'),
    path('gestion/canciones/<int:pk>/eliminar/', views.cancion_eliminar, name='cancion_eliminar'),
]
