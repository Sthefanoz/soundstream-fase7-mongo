"""
Modulo de Reportes (solo admin) - MongoDB.

En MongoDB el equivalente a los procedimientos/objetos programables de SQL son
los AGGREGATION PIPELINES: secuencias de etapas ($match, $group, $lookup,
$sort...) que la base ejecuta del lado del servidor. Cada reporte aqui es un
pipeline de solo lectura sobre las colecciones reales; el resultado se arma como
tabla generica (columnas + filas) y se renderiza con `web/reporte_tabla.html`.
"""

from django.db import connection
from django.shortcuts import render

from apps.catalogo.models import Artista, Album, Cancion
from apps.operacion.models import Reproduccion
from apps.usuarios.auth import admin_required
from apps.usuarios.models import Usuario, Playlist


def _db():
    """Base de datos pymongo subyacente (la misma conexion de Django)."""
    return connection.database


def _tabla(request, titulo, columnas, filas, subtitulo=''):
    return render(request, 'web/reporte_tabla.html', {
        'titulo': titulo,
        'columnas': columnas,
        'filas': filas,
        'subtitulo': subtitulo,
    })


def _money(x):
    return '${:,.2f}'.format(x or 0)


@admin_required
def panel(request):
    """Tablero del modulo de reportes: resumen + accesos a cada reporte."""
    return render(request, 'web/reportes_panel.html', {
        'n_artistas': Artista.objects.count(),
        'n_albumes': Album.objects.count(),
        'n_canciones': Cancion.objects.count(),
        'n_usuarios': Usuario.objects.count(),
        'n_playlists': Playlist.objects.count(),
        'n_reproducciones': Reproduccion.objects.count(),
    })


@admin_required
def top_canciones(request):
    pipeline = [
        {'$sort': {'numReproducciones': -1}},
        {'$limit': 25},
        {'$lookup': {'from': 'artistas', 'localField': 'artistaId',
                     'foreignField': '_id', 'as': 'art'}},
        {'$lookup': {'from': 'albumes', 'localField': 'albumId',
                     'foreignField': '_id', 'as': 'alb'}},
        {'$project': {
            'titulo': 1, 'numReproducciones': 1,
            'artista': {'$arrayElemAt': ['$art.nombreArtistico', 0]},
            'album': {'$arrayElemAt': ['$alb.titulo', 0]}}},
    ]
    filas = [[d.get('titulo'), d.get('artista'), d.get('album'),
              d.get('numReproducciones', 0)]
             for d in _db().canciones.aggregate(pipeline)]
    return _tabla(request, 'Top 25 canciones mas reproducidas',
                  ['Cancion', 'Artista', 'Album', 'Reproducciones'], filas)


@admin_required
def top_artistas(request):
    pipeline = [
        {'$group': {'_id': '$artistaId',
                    'plays': {'$sum': '$numReproducciones'},
                    'n': {'$sum': 1}}},
        {'$sort': {'plays': -1}},
        {'$limit': 25},
        {'$lookup': {'from': 'artistas', 'localField': '_id',
                     'foreignField': '_id', 'as': 'art'}},
        {'$project': {'plays': 1, 'n': 1,
                      'nombre': {'$arrayElemAt': ['$art.nombreArtistico', 0]}}},
    ]
    filas = [[d.get('nombre'), d.get('n', 0), d.get('plays', 0)]
             for d in _db().canciones.aggregate(pipeline)]
    return _tabla(request, 'Top 25 artistas por reproducciones',
                  ['Artista', 'Canciones', 'Reproducciones'], filas)


@admin_required
def ingresos_por_plan(request):
    pipeline = [
        {'$match': {'resultado': 'Aprobado'}},
        {'$lookup': {'from': 'suscripciones', 'localField': 'suscripcionId',
                     'foreignField': '_id', 'as': 'sus'}},
        {'$group': {'_id': {'$arrayElemAt': ['$sus.tipoPlan', 0]},
                    'total': {'$sum': '$monto'}, 'n': {'$sum': 1}}},
        {'$sort': {'total': -1}},
    ]
    datos = list(_db().pagos.aggregate(pipeline))
    filas = [[d.get('_id') or '-', d.get('n', 0), _money(d.get('total'))]
             for d in datos]
    total = sum(d.get('total') or 0 for d in datos)
    return _tabla(request, 'Ingresos por plan',
                  ['Plan', 'Pagos aprobados', 'Ingresos'], filas,
                  subtitulo=f'Ingresos totales (pagos aprobados): {_money(total)}')


@admin_required
def regalias_por_artista(request):
    pipeline = [
        {'$group': {'_id': '$artistaId',
                    'total': {'$sum': '$monto'}, 'n': {'$sum': 1}}},
        {'$sort': {'total': -1}},
        {'$lookup': {'from': 'artistas', 'localField': '_id',
                     'foreignField': '_id', 'as': 'art'}},
        {'$project': {'total': 1, 'n': 1,
                      'nombre': {'$arrayElemAt': ['$art.nombreArtistico', 0]}}},
    ]
    datos = list(_db().regalias.aggregate(pipeline))
    filas = [[d.get('nombre') or '-', d.get('n', 0), _money(d.get('total'))]
             for d in datos]
    total = sum(d.get('total') or 0 for d in datos)
    return _tabla(request, 'Regalias por artista',
                  ['Artista', 'Registros', 'Monto acumulado'], filas,
                  subtitulo=f'Total acumulado: {_money(total)}')


@admin_required
def reproducciones_por_pais(request):
    pipeline = [
        {'$group': {'_id': '$paisOrigen', 'n': {'$sum': 1}}},
        {'$sort': {'n': -1}},
    ]
    filas = [[d.get('_id') or 'Desconocido', d.get('n', 0)]
             for d in _db().reproducciones.aggregate(pipeline)]
    return _tabla(request, 'Reproducciones por pais',
                  ['Pais', 'Reproducciones'], filas)


@admin_required
def suscripciones_resumen(request):
    pipeline = [
        {'$group': {'_id': {'plan': '$tipoPlan', 'estado': '$estado'},
                    'n': {'$sum': 1}}},
        {'$sort': {'_id.plan': 1, '_id.estado': 1}},
    ]
    filas = [[d['_id'].get('plan'), d['_id'].get('estado') or '-', d.get('n', 0)]
             for d in _db().suscripciones.aggregate(pipeline)]
    return _tabla(request, 'Suscripciones por plan y estado',
                  ['Plan', 'Estado', 'Cantidad'], filas)
