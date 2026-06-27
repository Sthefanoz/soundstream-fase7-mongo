"""
Variables disponibles en todas las plantillas (branding, estadisticas globales).
"""

from django.db.models import Sum

from apps.catalogo.models import Cancion, Artista, Album


def branding(request):
    return {
        'BRAND': {
            'nombre': 'SoundStream',
            'tagline': 'Tu mundo. Tu sonido. Sin limites.',
            'email': 'contacto@soundstream.example',
            'instagram': 'https://instagram.com/soundstream',
            'twitter': 'https://twitter.com/soundstream',
            'tiktok': 'https://tiktok.com/@soundstream',
            'web_actual': 'www.soundstream.example',
        },
        'STATS': {
            'canciones': 50000000,
            'artistas': 50000,
            'podcasts': 100000,
        },
    }
