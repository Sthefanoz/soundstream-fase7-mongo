"""
Autenticacion propia contra Operacion.Usuario (sin el auth de Django).
El usuario logueado se guarda en la sesion (clave 'usuario_id').

Nota: las contrasenas en la BD de Fase 3 estan en texto plano, asi que se
comparan directamente. Si en el futuro se hashean, cambiar 'verificar_password'.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Usuario

SESSION_KEY = 'usuario_id'


def verificar_password(guardada, ingresada):
    return guardada == ingresada


def autenticar(email, password):
    """Devuelve el Usuario si las credenciales son validas, si no None."""
    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return None
    if verificar_password(usuario.password, password):
        return usuario
    return None


def login_usuario(request, usuario):
    request.session[SESSION_KEY] = usuario.id_usuario


def logout_usuario(request):
    request.session.pop(SESSION_KEY, None)


def get_usuario(request):
    """Usuario actual (o None). Se cachea en el request para no repetir queries."""
    if hasattr(request, '_usuario_cache'):
        return request._usuario_cache
    usuario = None
    uid = request.session.get(SESSION_KEY)
    if uid:
        usuario = Usuario.objects.filter(pk=uid).first()
    request._usuario_cache = usuario
    return usuario


def usuario_required(view):
    """Equivalente a login_required pero para nuestra auth por sesion."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not get_usuario(request):
            messages.error(request, 'Inicia sesion para continuar.')
            return redirect('web:login')
        return view(request, *args, **kwargs)
    return wrapper


def admin_required(view):
    """Solo permite el acceso a usuarios con rol 'admin'."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        usuario = get_usuario(request)
        if not usuario:
            messages.error(request, 'Inicia sesion para continuar.')
            return redirect('web:login')
        if not usuario.es_admin:
            messages.error(request, 'Necesitas permisos de administrador.')
            return redirect('web:inicio')
        return view(request, *args, **kwargs)
    return wrapper


def usuario_actual(request):
    """Context processor: expone 'usuario' en todas las plantillas."""
    return {'usuario': get_usuario(request)}
