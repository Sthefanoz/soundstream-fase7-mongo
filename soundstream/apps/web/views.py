"""
Vistas publicas con animaciones de scroll. Datos REALES de MongoDB Atlas.
Login/Logout usan la auth propia (apps.usuarios.auth) contra la coleccion
'usuarios'. Las agregaciones se hacen por coleccion (group/$sum) sobre el
campo de referencia (artistaId / albumId).
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.catalogo.models import Artista, Album, Cancion
from apps.common.ids import siguiente_id
from apps.operacion.models import Suscripcion, Pago, PeriodoFacturado
from apps.usuarios.auth import (autenticar, login_usuario, logout_usuario,
                                usuario_required, get_usuario)
from .forms import ContratarForm


PLANES_INFO = {
    'free': {'nombre': 'Free', 'precio': Decimal('0.00')},
    'premium': {'nombre': 'Premium', 'precio': Decimal('9.99')},
    'familiar': {'nombre': 'Familiar', 'precio': Decimal('14.99')},
}


def _conteo_por(modelo, campo_ref):
    """Devuelve {id_referencia: cantidad} agrupando una coleccion por un campo
    de referencia (p. ej. canciones por albumId)."""
    return {r[campo_ref]: r['n'] for r in
            modelo.objects.values(campo_ref).annotate(n=Count('pk'))}


def inicio(request):
    # Top artistas: suma de reproducciones de sus canciones (group por artistaId).
    plays_por_artista = {r['artista']: r['plays'] for r in
                         Cancion.objects.values('artista')
                         .annotate(plays=Sum('num_reproducciones'))}
    top_ids = sorted(plays_por_artista, key=plays_por_artista.get, reverse=True)[:6]
    top_artistas = list(Artista.objects.filter(id_artista__in=top_ids))
    top_artistas.sort(key=lambda a: plays_por_artista.get(a.pk, 0), reverse=True)
    for a in top_artistas:
        a.plays = plays_por_artista.get(a.pk, 0)

    nuevos_albumes = Album.objects.select_related('artista').order_by('-fecha_lanzamiento')[:8]
    top_canciones = (Cancion.objects.select_related('album__artista')
                     .order_by('-num_reproducciones')[:10])
    return render(request, 'web/inicio.html', {
        'top_artistas': top_artistas,
        'nuevos_albumes': nuevos_albumes,
        'top_canciones': top_canciones,
    })


def catalogo(request):
    query = request.GET.get('q', '').strip()
    qs = Cancion.objects.select_related('album__artista')
    if query:
        qs = qs.filter(titulo__icontains=query)
    canciones = qs.order_by('-num_reproducciones')[:60]
    return render(request, 'web/catalogo.html', {
        'canciones': canciones,
        'query': query,
    })


def artistas(request):
    artistas_qs = list(Artista.objects.order_by('nombre'))
    conteo = _conteo_por(Album, 'artista')
    for a in artistas_qs:
        a.total_albumes = conteo.get(a.pk, 0)
    return render(request, 'web/artistas.html', {'artistas': artistas_qs})


def albumes(request):
    albumes_qs = list(Album.objects.select_related('artista').order_by('-fecha_lanzamiento'))
    conteo = _conteo_por(Cancion, 'album')
    for al in albumes_qs:
        al.total_canciones = conteo.get(al.pk, 0)
    return render(request, 'web/albumes.html', {'albumes': albumes_qs})


def suscripciones(request):
    planes = [
        {
            'codigo': 'FREE', 'nombre': 'Free',
            'precio': '0', 'periodo': 'siempre',
            'features': [
                'Acceso al catalogo completo',
                'Calidad estandar 128 kbps',
                'Con anuncios cada 3 canciones',
                'Saltos limitados (6/hora)',
                'Sin descargas offline',
            ],
            'destacado': False,
        },
        {
            'codigo': 'PREMIUM', 'nombre': 'Premium',
            'precio': '9.99', 'periodo': '/mes',
            'features': [
                'Sin anuncios',
                'Calidad 320 kbps + FLAC lossless',
                'Saltos ilimitados',
                'Descarga offline',
                'Letras sincronizadas',
            ],
            'destacado': True,
        },
        {
            'codigo': 'FAMILIAR', 'nombre': 'Familiar',
            'precio': '14.99', 'periodo': '/mes',
            'features': [
                'Hasta 6 cuentas Premium',
                'Control parental',
                'Playlists colaborativas',
                'Calidad FLAC en todas las cuentas',
                'Soporte prioritario',
            ],
            'destacado': False,
        },
    ]
    return render(request, 'web/suscripciones.html', {'planes': planes})


def contacto(request):
    enviado = False
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        if nombre and email and mensaje:
            messages.success(request, 'Mensaje enviado. Te responderemos en 24h.')
            enviado = True
        else:
            messages.error(request, 'Completa todos los campos.')
    return render(request, 'web/contacto.html', {'enviado': enviado})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        usuario = autenticar(email, password)
        if usuario is not None:
            login_usuario(request, usuario)
            messages.success(request, f'Bienvenido, {usuario.primer_nombre}.')
            return redirect('web:inicio')
        messages.error(request, 'Correo o contrasena incorrectos.')
    return render(request, 'web/login.html')


def logout_view(request):
    logout_usuario(request)
    messages.success(request, 'Sesion cerrada.')
    return redirect('web:inicio')


@usuario_required
def contratar_plan(request, plan):
    """Contrata un plan: crea el documento Suscripcion (+ Pago si es de pago)."""
    info = PLANES_INFO.get(plan.lower())
    if not info:
        messages.error(request, 'Plan no valido.')
        return redirect('web:suscripciones')

    usuario = get_usuario(request)
    es_pago = info['precio'] > 0
    form = None

    if request.method == 'POST':
        if es_pago:
            form = ContratarForm(request.POST)
            if not form.is_valid():
                messages.error(request, 'Revisa los datos de pago.')
                return render(request, 'web/contratar.html',
                              {'plan': plan.lower(), 'info': info, 'form': form})
            metodo = form.cleaned_data['metodo_pago']
        else:
            metodo = None

        hoy = timezone.localdate()
        fin = (hoy + timedelta(days=30)).isoformat()
        # Vence la suscripcion activa anterior (un solo plan activo a la vez).
        Suscripcion.objects.filter(usuario=usuario, estado='Activa').update(estado='Vencida')

        suscripcion = Suscripcion(
            id_suscripcion=siguiente_id(Suscripcion),
            usuario=usuario,
            tipo_plan=info['nombre'],
            fecha_inicio=hoy.isoformat(),
            fecha_fin=fin,
            estado='Activa',
            precio_mensual=float(info['precio']),
            renovacion_automatica=True,
            fecha_creacion=timezone.now().replace(tzinfo=None).isoformat(),
        )
        suscripcion.save()

        # Marca esta como la suscripcion actual del usuario (campo embebido).
        usuario.suscripcion_actual_id = suscripcion.pk
        usuario.save(update_fields=['suscripcion_actual_id'])

        if es_pago:
            pago = Pago(
                id_pago=siguiente_id(Pago),
                monto=float(info['precio']),
                fecha_pago=timezone.now().replace(tzinfo=None).isoformat(),
                metodo_pago=metodo,
                resultado='Aprobado',
                usuario=usuario,
                suscripcion=suscripcion,
                periodo_facturado=PeriodoFacturado(
                    fecha_inicio=hoy.isoformat(), fecha_fin=fin),
                referencia_pago=f'REF-{siguiente_id(Pago):06d}',
                estado_pago='Aprobado',
            )
            pago.save()
            messages.success(request, f'Pago aprobado. Plan {info["nombre"]} activado.')
        else:
            messages.success(request, 'Plan Free activado.')
        return redirect('operacion:historial')

    if es_pago:
        form = ContratarForm()
    return render(request, 'web/contratar.html',
                  {'plan': plan.lower(), 'info': info, 'form': form})
