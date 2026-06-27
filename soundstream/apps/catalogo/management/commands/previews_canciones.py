"""
Comando: python manage.py previews_canciones [--solo-vacias]

Descarga la preview de audio (30s) de cada cancion desde la API publica de
Deezer y la guarda en el campo 'preview'. Tambien corrige la duracion con la
que reporta Deezer. No requiere API key.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.catalogo.deezer import buscar_track
from apps.catalogo.models import Cancion


class Command(BaseCommand):
    help = 'Descarga previews de audio y corrige duraciones desde Deezer.'

    def add_arguments(self, parser):
        parser.add_argument('--solo-vacias', action='store_true',
                            help='Solo procesa canciones que aun no tienen preview.')

    def handle(self, *args, **opts):
        qs = Cancion.objects.order_by('titulo')
        if opts['solo_vacias']:
            qs = qs.filter(Q(preview__isnull=True) | Q(preview=''))

        ok = fallidos = 0
        for cancion in qs:
            track = buscar_track(cancion.titulo, cancion.artista.nombre)
            if not track or not track.get('preview'):
                fallidos += 1
                self.stdout.write(self.style.WARNING(f'  sin preview: {cancion.titulo}'))
                continue

            cancion.preview = track['preview']
            segundos = int(track.get('duration') or 0)
            if 0 < segundos < 3600:
                cancion.duracion = f'00:{segundos // 60:02d}:{segundos % 60:02d}'
            cancion.save(update_fields=['preview', 'duracion'])
            ok += 1
            self.stdout.write(f'  OK  {cancion.titulo}  ({cancion.artista.nombre})')

        self.stdout.write(self.style.SUCCESS(f'Listo: {ok} con preview, {fallidos} sin preview.'))
