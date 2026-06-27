"""
Vistas de operacion: historial del usuario (reproducciones, suscripcion, pagos)
y reporte de regalias por artista. Lectura de datos reales de MongoDB.
"""

from django.db.models import Sum, Count
from django.shortcuts import render

from apps.catalogo.models import Artista
from apps.usuarios.auth import get_usuario, usuario_required
from .models import Reproduccion, Pago, Regalia, Suscripcion


@usuario_required
def historial_usuario(request):
    usuario = get_usuario(request)
    reproducciones = Reproduccion.objects.filter(usuario=usuario)[:50]
    suscripcion = (Suscripcion.objects
                   .filter(usuario=usuario)
                   .order_by('-fecha_inicio')
                   .first())
    # En Mongo el pago referencia directamente al usuario (usuarioId).
    pagos = Pago.objects.filter(usuario=usuario, resultado='Aprobado')
    return render(request, 'web/historial.html', {
        'reproducciones': reproducciones,
        'pagos': pagos,
        'suscripcion': suscripcion,
    })


def reporte_regalias(request):
    """Reporte: total de regalias acumuladas por artista (group por artistaId)."""
    por_artista = (Regalia.objects
                   .values('artista')
                   .annotate(total_monto=Sum('monto'), num_regalias=Count('pk'))
                   .order_by('-total_monto'))
    artistas = {a.pk: a for a in Artista.objects.filter(
        id_artista__in=[r['artista'] for r in por_artista])}
    resultados = []
    for r in por_artista:
        artista = artistas.get(r['artista'])
        if not artista:
            continue
        artista.total_monto = r['total_monto'] or 0
        artista.num_regalias = r['num_regalias']
        resultados.append(artista)
    total_global = Regalia.objects.aggregate(t=Sum('monto'))['t'] or 0
    return render(request, 'web/regalias.html', {
        'resultados': resultados,
        'total_global': total_global,
    })
