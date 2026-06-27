from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'apps.web'
    verbose_name = 'Frontend SoundStream'
