"""
Comando: python manage.py portadas_albumes [--solo-vacias]

Descarga portadas REALES de los albumes desde la API publica de Deezer
(https://api.deezer.com) y las guarda en Catalogo.Album.portada.
Busca por artista + titulo para mayor precision. No requiere API key.
"""

import json
import unicodedata
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.catalogo.models import Album


def normaliza(texto):
    t = unicodedata.normalize('NFD', texto or '')
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return t.lower().strip()


def buscar_en_deezer(consulta):
    url = 'https://api.deezer.com/search/album?' + urllib.parse.urlencode(
        {'q': consulta, 'limit': 5})
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.load(resp).get('data', [])
    except Exception:
        return []


def buscar_portada(titulo, artista):
    consultas = [
        f'artist:"{artista}" album:"{titulo}"',
        f'album:"{titulo}"',
        f'{artista} {titulo}',
    ]
    for consulta in consultas:
        resultados = buscar_en_deezer(consulta)
        if resultados:
            elegido = next(
                (a for a in resultados if normaliza(a['title']) == normaliza(titulo)),
                resultados[0])
            return elegido.get('cover_xl') or elegido.get('cover_big') or elegido.get('cover')
    return None


class Command(BaseCommand):
    help = 'Descarga portadas de los albumes desde la API publica de Deezer.'

    def add_arguments(self, parser):
        parser.add_argument('--solo-vacias', action='store_true',
                            help='Solo busca portada para los albumes que aun no tienen.')

    def handle(self, *args, **opts):
        qs = Album.objects.order_by('titulo')
        if opts['solo_vacias']:
            qs = qs.filter(Q(portada__isnull=True) | Q(portada=''))

        ok = fallidos = 0
        for album in qs:
            portada = buscar_portada(album.titulo, album.artista.nombre)
            if portada:
                album.portada = portada
                album.save(update_fields=['portada'])
                ok += 1
                self.stdout.write(f'  OK  {album.titulo}  ({album.artista.nombre})')
            else:
                fallidos += 1
                self.stdout.write(self.style.WARNING(
                    f'  sin coincidencia: {album.titulo} ({album.artista.nombre})'))

        self.stdout.write(self.style.SUCCESS(f'Listo: {ok} con portada, {fallidos} sin portada.'))
