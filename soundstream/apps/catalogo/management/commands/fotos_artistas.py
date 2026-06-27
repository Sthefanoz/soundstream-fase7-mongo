"""
Comando: python manage.py fotos_artistas [--solo-vacias]

Descarga fotos REALES de los artistas desde la API publica de Deezer
(https://api.deezer.com) y las guarda en la columna Catalogo.Artista.foto.
No requiere API key. Las URLs provienen del catalogo de Deezer, no se inventan.
"""

import json
import unicodedata
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.catalogo.models import Artista


def normaliza(texto):
    t = unicodedata.normalize('NFD', texto or '')
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return t.lower().strip()


class Command(BaseCommand):
    help = 'Descarga fotos de los artistas desde la API publica de Deezer.'

    def add_arguments(self, parser):
        parser.add_argument('--solo-vacias', action='store_true',
                            help='Solo busca foto para los artistas que aun no tienen.')

    def handle(self, *args, **opts):
        qs = Artista.objects.all().order_by('nombre')
        if opts['solo_vacias']:
            qs = qs.filter(Q(foto__isnull=True) | Q(foto=''))

        ok = fallidos = 0
        for artista in qs:
            url = 'https://api.deezer.com/search/artist?' + urllib.parse.urlencode(
                {'q': artista.nombre, 'limit': 5})
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    data = json.load(resp)
            except Exception as exc:
                fallidos += 1
                self.stdout.write(self.style.ERROR(f'  error {artista.nombre}: {exc}'))
                continue

            resultados = data.get('data', [])
            if not resultados:
                fallidos += 1
                self.stdout.write(self.style.WARNING(f'  sin coincidencia: {artista.nombre}'))
                continue

            elegido = next(
                (a for a in resultados if normaliza(a['name']) == normaliza(artista.nombre)),
                resultados[0])
            foto = elegido.get('picture_xl') or elegido.get('picture_big') or elegido.get('picture')
            artista.foto = foto
            artista.save(update_fields=['foto'])
            ok += 1
            self.stdout.write(f'  OK  {artista.nombre}  ->  {elegido["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Listo: {ok} con foto, {fallidos} sin foto.'))
