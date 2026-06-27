"""
Usuario y Playlist en MongoDB (SoundStreamDB_NoSQL).

Diseño NoSQL: el usuario embebe arreglos de ids (cancionesGuardadas,
albumesGuardados, artistasSeguidos) y la playlist embebe un arreglo de ids de
canciones ('canciones'). No hay tabla puente: la relacion playlist-cancion vive
como arreglo dentro del documento de la playlist.
"""

from django.db import models

from django_mongodb_backend.fields import ArrayField

from apps.catalogo.models import Cancion


class Usuario(models.Model):
    id_usuario = models.IntegerField(primary_key=True, db_column='_id')
    primer_nombre = models.CharField(max_length=50, db_column='primerNombre')
    primer_apellido = models.CharField(max_length=50, db_column='primerApellido')
    email = models.CharField(max_length=120)
    password = models.CharField(max_length=255)
    pais = models.CharField(max_length=50, blank=True, null=True)
    fecha_registro = models.CharField(max_length=20, db_column='fechaRegistro',
                                      blank=True, null=True)
    estado_cuenta = models.CharField(max_length=20, db_column='estadoCuenta',
                                     default='Activo', blank=True, null=True)
    rol = models.CharField(max_length=20, default='usuario')
    canciones_guardadas = ArrayField(models.IntegerField(),
                                     db_column='cancionesGuardadas', blank=True, null=True)
    albumes_guardados = ArrayField(models.IntegerField(),
                                   db_column='albumesGuardados', blank=True, null=True)
    artistas_seguidos = ArrayField(models.IntegerField(),
                                   db_column='artistasSeguidos', blank=True, null=True)
    suscripcion_actual_id = models.IntegerField(db_column='suscripcionActualId',
                                                blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'
        ordering = ['primer_nombre', 'primer_apellido']

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self):
        return f'{self.primer_nombre} {self.primer_apellido}'

    @property
    def es_admin(self):
        return (self.rol or '').lower() == 'admin'


class Playlist(models.Model):
    VISIBILIDAD = [
        ('publica', 'Publica'),
        ('privada', 'Privada'),
    ]

    id_playlist = models.IntegerField(primary_key=True, db_column='_id')
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo_visibilidad = models.CharField(max_length=20, choices=VISIBILIDAD,
                                        default='publica', db_column='tipoVisibilidad')
    canciones_ids = ArrayField(models.IntegerField(), db_column='canciones',
                               blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='usuarioId', related_name='playlists')

    class Meta:
        managed = False
        db_table = 'playlists'
        ordering = ['-id_playlist']

    def __str__(self):
        return self.nombre

    @property
    def es_publica(self):
        return (self.tipo_visibilidad or '').lower() == 'publica'

    @property
    def canciones(self):
        """Canciones de la playlist a partir del arreglo de ids embebido."""
        ids = self.canciones_ids or []
        return Cancion.objects.filter(id_cancion__in=ids)
