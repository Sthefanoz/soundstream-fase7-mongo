"""
Helper compartido para consultar la API publica de Deezer (sin API key).

Lo usan tanto el comando `previews_canciones` (carga masiva) como la vista
`preview_cancion` (resolucion en vivo al momento de reproducir), de modo que
la URL de preview siempre este fresca y la cancion siempre se pueda reproducir.
"""

import json
import unicodedata
import urllib.parse
import urllib.request


def normaliza(texto):
    t = unicodedata.normalize('NFD', texto or '')
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return t.lower().strip()


def buscar_track(titulo, artista, timeout=15):
    """Devuelve el dict del track de Deezer que mejor coincide, o None."""
    consultas = [
        f'artist:"{artista}" track:"{titulo}"',
        f'track:"{titulo}"',
        f'{artista} {titulo}',
    ]
    for consulta in consultas:
        url = 'https://api.deezer.com/search/track?' + urllib.parse.urlencode(
            {'q': consulta, 'limit': 5})
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                resultados = json.load(resp).get('data', [])
        except Exception:
            resultados = []
        if resultados:
            return next(
                (t for t in resultados if normaliza(t['title']) == normaliza(titulo)),
                resultados[0])
    return None
