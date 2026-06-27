"""
Configuracion de Django para el proyecto SoundStream.
Fase 7 - Proyecto Integrador.
"""

import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-soundstream-fase7-cambia-esto-en-produccion'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.catalogo',
    'apps.operacion',
    'apps.reportes',
    'apps.usuarios',
    'apps.web',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soundstream.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'apps.web.context_processors.branding',
                'apps.usuarios.auth.usuario_actual',
            ],
        },
    },
]

WSGI_APPLICATION = 'soundstream.wsgi.application'

# ---------------------------------------------------------------------------
# BASE DE DATOS - MongoDB Atlas (NoSQL)
# ---------------------------------------------------------------------------
# Por seguridad, la cadena de conexion NO se escribe aqui: se lee de un archivo
# JSON externo que queda fuera del control de versiones (db_config.json,
# ignorado en .gitignore). Asi las credenciales del cluster no se exponen en el
# codigo. Copia 'db_config.example.json' a 'db_config.json' y coloca tu URI de
# Atlas y el nombre de la base. La ruta se puede sobreescribir con la variable
# de entorno SOUNDSTREAM_DB_CONFIG.
import django_mongodb_backend

DB_CONFIG_PATH = Path(
    os.environ.get('SOUNDSTREAM_DB_CONFIG', BASE_DIR / 'db_config.json'))

if not DB_CONFIG_PATH.exists():
    raise ImproperlyConfigured(
        f"No se encontro el archivo de configuracion de la BD: {DB_CONFIG_PATH}\n"
        "Copia 'db_config.example.json' a 'db_config.json' y coloca tu cadena de "
        "conexion de MongoDB Atlas (URI) y el nombre de la base (NAME)."
    )

try:
    with open(DB_CONFIG_PATH, encoding='utf-8') as _f:
        _db = json.load(_f)
except (json.JSONDecodeError, OSError) as exc:
    raise ImproperlyConfigured(
        f"No se pudo leer '{DB_CONFIG_PATH}': {exc}") from exc

if not _db.get('URI'):
    raise ImproperlyConfigured(
        "Falta 'URI' en db_config.json (cadena mongodb+srv://... de Atlas).")

# parse_uri arma el diccionario de conexion que entiende django-mongodb-backend.
DATABASES = {
    'default': django_mongodb_backend.parse_uri(
        _db['URI'], db_name=_db.get('NAME', 'soundstream')),
}

# En MongoDB las claves primarias son ObjectId, no enteros autoincrementales.
DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

FIXTURE_DIRS = [BASE_DIR / 'fixtures']

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
