"""
Operacion en MongoDB (SoundStreamDB_NoSQL):
Suscripcion, Pago (con periodo facturado embebido), Reproduccion y Regalia.

managed = False -> mapean a las colecciones existentes.
Las fechas se guardan como texto ISO (asi estan en los documentos).
"""

from django.db import models

from django_mongodb_backend.fields import EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel

from apps.catalogo.models import Cancion, Artista
from apps.usuarios.models import Usuario


class Suscripcion(models.Model):
    id_suscripcion = models.IntegerField(primary_key=True, db_column='_id')
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='usuarioId', related_name='suscripciones')
    tipo_plan = models.CharField(max_length=30, db_column='tipoPlan')
    fecha_inicio = models.CharField(max_length=20, db_column='fechaInicio',
                                    blank=True, null=True)
    fecha_fin = models.CharField(max_length=20, db_column='fechaFin',
                                 blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    precio_mensual = models.FloatField(db_column='precioMensual', blank=True, null=True)
    renovacion_automatica = models.BooleanField(db_column='renovacionAutomatica',
                                                default=False)
    fecha_creacion = models.CharField(max_length=30, db_column='fechaCreacion',
                                      blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suscripciones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.tipo_plan} ({self.estado})'

    @property
    def activa(self):
        return (self.estado or '').lower() == 'activa'


class PeriodoFacturado(EmbeddedModel):
    """Documento embebido dentro de cada pago."""
    fecha_inicio = models.CharField(max_length=20, db_column='fechaInicio',
                                    blank=True, null=True)
    fecha_fin = models.CharField(max_length=20, db_column='fechaFin',
                                 blank=True, null=True)


class Pago(models.Model):
    id_pago = models.IntegerField(primary_key=True, db_column='_id')
    monto = models.FloatField()
    fecha_pago = models.CharField(max_length=30, db_column='fechaPago',
                                  blank=True, null=True)
    metodo_pago = models.CharField(max_length=40, db_column='metodoPago',
                                   blank=True, null=True)
    resultado = models.CharField(max_length=20, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='usuarioId', related_name='pagos')
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.DO_NOTHING,
                                    db_column='suscripcionId', related_name='pagos',
                                    blank=True, null=True)
    periodo_facturado = EmbeddedModelField(PeriodoFacturado,
                                           db_column='periodoFacturado',
                                           blank=True, null=True)
    referencia_pago = models.CharField(max_length=40, db_column='referenciaPago',
                                       blank=True, null=True)
    estado_pago = models.CharField(max_length=20, db_column='estadoPago',
                                   blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pagos'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f'#{self.id_pago} - {self.monto}'

    @property
    def aprobado(self):
        return (self.resultado or '').lower() == 'aprobado'


class Reproduccion(models.Model):
    id_reproduccion = models.IntegerField(primary_key=True, db_column='_id')
    fecha = models.CharField(max_length=30, blank=True, null=True)
    tiempo_escuchado = models.CharField(max_length=30, db_column='tiempoEscuchado',
                                        blank=True, null=True)
    pais_origen = models.CharField(max_length=50, db_column='paisOrigen',
                                   blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='usuarioId', related_name='reproducciones')
    cancion = models.ForeignKey(Cancion, on_delete=models.DO_NOTHING,
                                db_column='cancionId', related_name='reproducciones')

    class Meta:
        managed = False
        db_table = 'reproducciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'Reproduccion #{self.id_reproduccion}'


class Regalia(models.Model):
    id_regalia = models.IntegerField(primary_key=True, db_column='_id')
    monto = models.FloatField()
    fecha_calculo = models.CharField(max_length=20, db_column='fechaCalculo',
                                     blank=True, null=True)
    reproduccion = models.ForeignKey(Reproduccion, on_delete=models.DO_NOTHING,
                                     db_column='reproduccionId', null=True, blank=True,
                                     related_name='regalias')
    cancion = models.ForeignKey(Cancion, on_delete=models.DO_NOTHING,
                                db_column='cancionId', null=True, blank=True,
                                related_name='regalias')
    artista = models.ForeignKey(Artista, on_delete=models.DO_NOTHING,
                                db_column='artistaId', null=True, blank=True,
                                related_name='regalias')

    class Meta:
        managed = False
        db_table = 'regalias'
        ordering = ['-fecha_calculo']

    def __str__(self):
        return f'Regalia #{self.id_regalia} - {self.monto}'
