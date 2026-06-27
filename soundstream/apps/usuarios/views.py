"""
Registro de Usuario y CRUD de Playlist (coleccion 'playlists' en MongoDB).

Diseño NoSQL: la relacion playlist-cancion vive como un arreglo de ids de
cancion ('canciones') embebido en el documento de la playlist; agregar/quitar
canciones es modificar ese arreglo (no hay tabla puente).
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.catalogo.models import Cancion
from apps.common.ids import siguiente_id
from .auth import get_usuario, login_usuario, usuario_required
from .forms import RegistroForm, PlaylistForm
from .models import Playlist


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.id_usuario = siguiente_id(type(usuario))
            usuario.save()
            login_usuario(request, usuario)
            messages.success(request, 'Cuenta creada. Bienvenido a SoundStream.')
            return redirect('web:inicio')
    else:
        form = RegistroForm()
    return render(request, 'web/registro.html', {'form': form})


@usuario_required
def mis_playlists(request):
    playlists = Playlist.objects.filter(usuario=get_usuario(request))
    return render(request, 'web/playlists.html', {
        'playlists': playlists,
        'es_propio': True,
    })


def playlists_publicas(request):
    playlists = Playlist.objects.filter(tipo_visibilidad='publica')[:30]
    return render(request, 'web/playlists.html', {
        'playlists': playlists,
        'es_propio': False,
    })


@usuario_required
def crear_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.id_playlist = siguiente_id(Playlist)
            playlist.usuario = get_usuario(request)
            playlist.canciones_ids = []
            playlist.save()
            messages.success(request, f'Playlist "{playlist.nombre}" creada.')
            return redirect('usuarios:detalle_playlist', playlist_id=playlist.id_playlist)
    else:
        form = PlaylistForm()
    return render(request, 'web/playlist_form.html', {'form': form})


@usuario_required
def editar_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, f'Playlist "{playlist.nombre}" actualizada.')
            return redirect('usuarios:mis_playlists')
    else:
        form = PlaylistForm(instance=playlist)
    return render(request, 'web/playlist_form.html', {
        'form': form,
        'playlist': playlist,
    })


@usuario_required
@require_http_methods(['POST'])
def eliminar_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    nombre = playlist.nombre
    playlist.delete()
    messages.success(request, f'Playlist "{nombre}" eliminada.')
    return redirect('usuarios:mis_playlists')


@usuario_required
def detalle_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    ids_actuales = playlist.canciones_ids or []
    canciones = Cancion.objects.filter(id_cancion__in=ids_actuales)
    disponibles = (Cancion.objects
                   .exclude(id_cancion__in=ids_actuales)
                   .order_by('titulo'))
    return render(request, 'web/playlist_detalle.html', {
        'playlist': playlist,
        'canciones': canciones,
        'disponibles': disponibles,
    })


@usuario_required
@require_http_methods(['POST'])
def agregar_cancion(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    cancion = get_object_or_404(Cancion, pk=request.POST.get('cancion_id'))
    ids = playlist.canciones_ids or []
    if cancion.pk not in ids:
        ids.append(cancion.pk)
        playlist.canciones_ids = ids
        playlist.save(update_fields=['canciones_ids'])
        messages.success(request, f'"{cancion.titulo}" agregada a la playlist.')
    return redirect('usuarios:detalle_playlist', playlist_id=playlist.id_playlist)


@usuario_required
@require_http_methods(['POST'])
def quitar_cancion(request, playlist_id, cancion_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    ids = playlist.canciones_ids or []
    cid = int(cancion_id)
    if cid in ids:
        ids.remove(cid)
        playlist.canciones_ids = ids
        playlist.save(update_fields=['canciones_ids'])
    messages.success(request, 'Cancion quitada de la playlist.')
    return redirect('usuarios:detalle_playlist', playlist_id=playlist.id_playlist)
