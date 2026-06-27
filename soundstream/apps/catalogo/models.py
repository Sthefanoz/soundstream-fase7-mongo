"""
Modelos del catalogo en MongoDB (SoundStreamDB_NoSQL).

managed = False -> Django NO crea ni migra las colecciones; ya existen.
db_table  -> nombre de la coleccion en Mongo.
db_column -> nombre real del campo en el documento (camelCase).

Diseño NoSQL: 'discografica' va embebida en cada artista, y 'generos' es un
arreglo dentro de cada cancion (no son colecciones aparte).
"""

from django.db import models

from django_mongodb_backend.fields import ArrayField, EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel


def _segundos_desde_texto(texto):
    """Convierte 'HH:MM:SS.fffffff' a segundos enteros (0 si no se puede)."""
    if not texto:
        return 0
    try:
        h, m, s = str(texto).split(':')
        return int(h) * 3600 + int(m) * 60 + int(float(s))
    except (ValueError, AttributeError):
        return 0


class Discografica(EmbeddedModel):
    """Documento embebido dentro de cada artista (no es coleccion propia)."""
    nombre = models.CharField(max_length=80, db_column='nombreDiscografica',
                              blank=True, null=True)
    pais = models.CharField(max_length=40, blank=True, null=True)
    fecha_fundacion = models.CharField(max_length=20, db_column='fechaFundacion',
                                       blank=True, null=True)

    def __str__(self):
        return self.nombre or ''


class Artista(models.Model):
    id_artista = models.IntegerField(primary_key=True, db_column='_id')
    nombre = models.CharField(max_length=120, db_column='nombreArtistico')
    biografia = models.TextField(blank=True, null=True)
    foto = models.CharField(max_length=500, blank=True, null=True)
    discografica = EmbeddedModelField(Discografica, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artistas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Album(models.Model):
    id_album = models.IntegerField(primary_key=True, db_column='_id')
    titulo = models.CharField(max_length=200)
    fecha_lanzamiento = models.CharField(max_length=20, db_column='fechaLanzamiento',
                                         blank=True, null=True)
    portada = models.CharField(max_length=500, blank=True, null=True)
    artista = models.ForeignKey(Artista, on_delete=models.DO_NOTHING,
                                db_column='artistaId', related_name='albumes')

    class Meta:
        managed = False
        db_table = 'albumes'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def anio(self):
        return (self.fecha_lanzamiento or '')[:4]


class Cancion(models.Model):
    id_cancion = models.IntegerField(primary_key=True, db_column='_id')
    titulo = models.CharField(max_length=200)
    duracion = models.CharField(max_length=30, blank=True, null=True)
    calidad_audio = models.CharField(max_length=20, db_column='calidadAudio',
                                     blank=True, null=True)
    num_reproducciones = models.IntegerField(default=0, db_column='numReproducciones')
    preview = models.CharField(max_length=500, blank=True, null=True)
    generos = ArrayField(models.CharField(max_length=60), blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.DO_NOTHING,
                              db_column='albumId', related_name='canciones')
    artista = models.ForeignKey(Artista, on_delete=models.DO_NOTHING,
                                db_column='artistaId', related_name='canciones')

    class Meta:
        managed = False
        db_table = 'canciones'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def duracion_mmss(self):
        total = _segundos_desde_texto(self.duracion)
        return f'{total // 60}:{total % 60:02d}'

    @property
    def es_flac(self):
        return (self.calidad_audio or '').upper() == 'FLAC'
