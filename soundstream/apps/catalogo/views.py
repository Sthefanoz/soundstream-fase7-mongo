"""
Vistas de Catalogo (MongoDB):
- Publicas: detalle de artista/album y registro de reproduccion.
- Panel admin (solo rol 'admin'): CRUD de Artista, Album y Cancion.

Las escrituras usan el ORM normal de Django sobre las colecciones de Mongo.
Como los _id son enteros (no autoincrementales), al insertar calculamos el
siguiente id con apps.common.ids.siguiente_id.
"""

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.common.ids import siguiente_id
from apps.usuarios.auth import get_usuario, admin_required
from .deezer import buscar_track
from .forms import ArtistaForm, AlbumForm, CancionForm
from .models import Artista, Album, Cancion, Discografica


# ----------------------------------------------------------------------------
# Vistas publicas
# ----------------------------------------------------------------------------
def detalle_artista(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    albumes = artista.albumes.all()
    return render(request, 'web/artista_detalle.html', {
        'artista': artista,
        'albumes': albumes,
    })


def detalle_album(request, pk):
    album = get_object_or_404(Album, pk=pk)
    canciones = album.canciones.all()
    return render(request, 'web/album_detalle.html', {
        'album': album,
        'canciones': canciones,
    })


@require_http_methods(['POST'])
def reproducir_cancion(request, pk):
    """Incrementa numReproducciones e inserta un documento de Reproduccion."""
    from apps.operacion.models import Reproduccion

    usuario = get_usuario(request)
    if usuario is None:
        return JsonResponse({'ok': False, 'error': 'login'}, status=401)

    cancion = get_object_or_404(Cancion, pk=pk)
    cancion.num_reproducciones = (cancion.num_reproducciones or 0) + 1
    cancion.save(update_fields=['num_reproducciones'])

    Reproduccion(
        id_reproduccion=siguiente_id(Reproduccion),
        fecha=timezone.now().replace(tzinfo=None).isoformat(),
        tiempo_escuchado=cancion.duracion or '00:03:00',
        pais_origen=(usuario.pais or 'Ecuador'),
        usuario=usuario,
        cancion=cancion,
    ).save()

    return JsonResponse({
        'ok': True,
        'cancion': cancion.titulo,
        'reproducciones': cancion.num_reproducciones,
    })


def preview_cancion(request, pk):
    """Resuelve la preview de Deezer EN VIVO al momento de reproducir.

    Las URLs de preview de Deezer caducan, asi que en cada play se pide una
    fresca y se cachea en el documento. Si no hay internet o Deezer no
    responde, cae a la preview ya guardada.
    """
    cancion = get_object_or_404(Cancion, pk=pk)

    track = buscar_track(cancion.titulo, cancion.artista.nombre)
    preview = (track or {}).get('preview')

    if preview:
        cancion.preview = preview
        segundos = int((track.get('duration') or 0))
        if 0 < segundos < 3600:
            cancion.duracion = f'00:{segundos // 60:02d}:{segundos % 60:02d}'
        cancion.save(update_fields=['preview', 'duracion'])
    else:
        preview = cancion.preview or ''

    return JsonResponse({
        'ok': bool(preview),
        'preview': preview,
        'cancion': cancion.titulo,
    })


# ----------------------------------------------------------------------------
# Panel de administracion (solo admin)
# ----------------------------------------------------------------------------
@admin_required
def gestion_panel(request):
    return render(request, 'web/gestion_panel.html', {
        'n_artistas': Artista.objects.count(),
        'n_albumes': Album.objects.count(),
        'n_canciones': Cancion.objects.count(),
    })


@admin_required
def gestion_artistas(request):
    q = request.GET.get('q', '').strip()
    artistas = Artista.objects.all()
    if q:
        artistas = artistas.filter(nombre__icontains=q)
    filas = [{
        'pk': a.id_artista,
        'campos': [a.nombre, a.discografica.nombre if a.discografica else '-',
                   a.albumes.count()],
    } for a in artistas]
    return render(request, 'web/gestion_lista.html', {
        'titulo': 'Artistas', 'singular': 'artista', 'q': q,
        'columnas': ['Nombre', 'Discografica', 'Albumes'],
        'filas': filas,
        'url_nuevo': 'catalogo:artista_nuevo',
        'url_editar': 'catalogo:artista_editar',
        'url_eliminar': 'catalogo:artista_eliminar',
    })


@admin_required
def artista_form(request, pk=None):
    instancia = get_object_or_404(Artista, pk=pk) if pk else None
    if request.method == 'POST':
        form = ArtistaForm(request.POST, instance=instancia)
        if form.is_valid():
            artista = form.save(commit=False)
            if not instancia:
                artista.id_artista = siguiente_id(Artista)
            nombre_disco = form.cleaned_data['discografica_nombre']
            artista.discografica = (
                Discografica(nombre=nombre_disco) if nombre_disco else None)
            artista.save()
            messages.success(request, 'Artista guardado correctamente.')
            return redirect('catalogo:gestion_artistas')
    else:
        form = ArtistaForm(instance=instancia)
    return render(request, 'web/gestion_form.html', {
        'form': form, 'titulo': 'artista', 'es_edicion': instancia is not None,
        'url_volver': 'catalogo:gestion_artistas',
    })


@admin_required
@require_http_methods(['POST'])
def artista_eliminar(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    artista.delete()
    messages.success(request, 'Artista eliminado.')
    return redirect('catalogo:gestion_artistas')


@admin_required
def gestion_albumes(request):
    q = request.GET.get('q', '').strip()
    albumes = Album.objects.all()
    if q:
        albumes = albumes.filter(titulo__icontains=q)
    filas = [{
        'pk': al.id_album,
        'campos': [al.titulo, al.artista.nombre, al.anio, al.canciones.count()],
    } for al in albumes]
    return render(request, 'web/gestion_lista.html', {
        'titulo': 'Albumes', 'singular': 'album', 'q': q,
        'columnas': ['Titulo', 'Artista', 'Anio', 'Canciones'],
        'filas': filas,
        'url_nuevo': 'catalogo:album_nuevo',
        'url_editar': 'catalogo:album_editar',
        'url_eliminar': 'catalogo:album_eliminar',
    })


@admin_required
def album_form(request, pk=None):
    instancia = get_object_or_404(Album, pk=pk) if pk else None
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=instancia)
        if form.is_valid():
            album = form.save(commit=False)
            if not instancia:
                album.id_album = siguiente_id(Album)
            album.save()
            messages.success(request, 'Album guardado correctamente.')
            return redirect('catalogo:gestion_albumes')
    else:
        form = AlbumForm(instance=instancia)
    return render(request, 'web/gestion_form.html', {
        'form': form, 'titulo': 'album', 'es_edicion': instancia is not None,
        'url_volver': 'catalogo:gestion_albumes',
    })


@admin_required
@require_http_methods(['POST'])
def album_eliminar(request, pk):
    album = get_object_or_404(Album, pk=pk)
    album.delete()
    messages.success(request, 'Album eliminado.')
    return redirect('catalogo:gestion_albumes')


@admin_required
def gestion_canciones(request):
    q = request.GET.get('q', '').strip()
    canciones = Cancion.objects.all()
    if q:
        canciones = canciones.filter(titulo__icontains=q)
    canciones = canciones[:200]
    filas = [{
        'pk': c.id_cancion,
        'campos': [c.titulo, c.album.titulo, c.artista.nombre,
                   c.calidad_audio, c.num_reproducciones],
    } for c in canciones]
    return render(request, 'web/gestion_lista.html', {
        'titulo': 'Canciones', 'singular': 'cancion', 'q': q,
        'columnas': ['Titulo', 'Album', 'Artista', 'Calidad', 'Reproducciones'],
        'filas': filas,
        'url_nuevo': 'catalogo:cancion_nuevo',
        'url_editar': 'catalogo:cancion_editar',
        'url_eliminar': 'catalogo:cancion_eliminar',
    })


@admin_required
def cancion_form(request, pk=None):
    instancia = get_object_or_404(Cancion, pk=pk) if pk else None
    if request.method == 'POST':
        form = CancionForm(request.POST, instance=instancia)
        if form.is_valid():
            cancion = form.save(commit=False)
            if not instancia:
                cancion.id_cancion = siguiente_id(Cancion)
                cancion.num_reproducciones = 0
                cancion.generos = cancion.generos or []
            # El artista se denormaliza desde el album elegido.
            cancion.artista = cancion.album.artista
            cancion.save()
            messages.success(request, 'Cancion guardada correctamente.')
            return redirect('catalogo:gestion_canciones')
    else:
        form = CancionForm(instance=instancia)
    return render(request, 'web/gestion_form.html', {
        'form': form, 'titulo': 'cancion', 'es_edicion': instancia is not None,
        'url_volver': 'catalogo:gestion_canciones',
    })


@admin_required
@require_http_methods(['POST'])
def cancion_eliminar(request, pk):
    cancion = get_object_or_404(Cancion, pk=pk)
    cancion.delete()
    messages.success(request, 'Cancion eliminada.')
    return redirect('catalogo:gestion_canciones')
