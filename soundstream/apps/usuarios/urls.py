from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('playlists/mias/', views.mis_playlists, name='mis_playlists'),
    path('playlists/publicas/', views.playlists_publicas, name='publicas'),
    path('playlists/nueva/', views.crear_playlist, name='crear_playlist'),
    path('playlists/<int:playlist_id>/', views.detalle_playlist, name='detalle_playlist'),
    path('playlists/<int:playlist_id>/editar/', views.editar_playlist, name='editar_playlist'),
    path('playlists/<int:playlist_id>/eliminar/', views.eliminar_playlist, name='eliminar_playlist'),
    path('playlists/<int:playlist_id>/agregar/', views.agregar_cancion, name='agregar_cancion'),
    path('playlists/<int:playlist_id>/quitar/<int:cancion_id>/', views.quitar_cancion, name='quitar_cancion'),
]
