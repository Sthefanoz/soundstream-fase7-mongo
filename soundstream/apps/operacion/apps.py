from django.apps import AppConfig


class OperacionConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'apps.operacion'
    verbose_name = 'Operacion (reproducciones, pagos, regalias)'
