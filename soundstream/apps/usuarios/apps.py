from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios y Playlists'
