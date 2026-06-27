"""
Comando: python manage.py seed

Ya NO se usa. La aplicacion trabaja directamente sobre la base de datos real de
la Fase 3 (SoundStreamDB en SQL Server), cuyos datos ya estan cargados
(50 artistas, 100 canciones, 50 usuarios, etc.). Los modelos son managed=False,
asi que Django no crea ni puebla tablas: solo lee/escribe las existentes.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Obsoleto: los datos ya estan en SoundStreamDB (Fase 3).'

    def handle(self, *args, **opts):
        self.stdout.write(self.style.WARNING(
            'No es necesario sembrar datos: la app usa la BD real de Fase 3 '
            '(SoundStreamDB) con sus datos ya cargados.'))
