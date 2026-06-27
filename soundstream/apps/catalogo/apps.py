from django.apps import AppConfig


class CatalogoConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'apps.catalogo'
    verbose_name = 'Catalogo Musical'
