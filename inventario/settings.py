import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO (Usando Decouple)
# ==============================================================================
# decouple busca automáticamente el archivo .env en la raíz del proyecto.
# Asegúrate de que tu .env contenga todas estas variables.

SECRET_KEY = config('SECRET_KEY')

# El cast=bool convierte el 'True' o 'False' del .env a un booleano de Python.
DEBUG = config('DEBUG', default=False, cast=bool)

# El cast=Csv convierte 'host1,host2' del .env a una lista de Python.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())


# ==============================================================================
# APLICACIONES
# ==============================================================================
INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones Locales
    'gestion_activos',

    # Aplicaciones de Terceros
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # 'allauth.socialaccount.providers.google', # Descomenta si usas login con Google
    'anymail',
]

SITE_ID = 1

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise se recomienda colocarlo justo después de SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'inventario.urls'

# ==============================================================================
# PLANTILLAS (TEMPLATES)
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Carpeta de plantillas a nivel de proyecto
        'APP_DIRS': True, # Busca plantillas dentro de las carpetas 'templates' de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventario.wsgi.application'

# ==============================================================================
# BASE DE DATOS
# ==============================================================================
# dj_database_url leerá automáticamente la variable de entorno 'DATABASE_URL'.
# ¡No hay URLs de base de datos escritas en el código, lo cual es más seguro!
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=config('DB_SSL_REQUIRE', default=True, cast=bool)
    )
}

# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# AUTENTICACIÓN
# ==============================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = 'login'
# La redirección después del login ahora se maneja en la vista 'login_view'
# por lo que este valor es un fallback.
LOGIN_REDIRECT_URL = 'lista_activos'
LOGOUT_REDIRECT_URL = 'login'

# ==============================================================================
# INTERNACIONALIZACIÓN
# ==============================================================================
LANGUAGE_CODE = 'es-ve' # Código para español de Venezuela
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True # Mantenlo en True para manejar correctamente las zonas horarias

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==============================================================================
STATIC_URL = '/static/'

# Directorio donde `collectstatic` reunirá todos los archivos estáticos para producción.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# *** CONFIGURACIÓN SIMPLIFICADA ***
# Directorios adicionales donde Django buscará archivos estáticos.
# Ahora apunta a una única carpeta 'static' en la raíz del proyecto.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Almacenamiento optimizado para WhiteNoise en producción.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_dir / 'media'

# ==============================================================================
# CONFIGURACIÓN DE CORREO (Anymail con Postmark)
# ==============================================================================
EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
ANYMAIL = {
    # Lee el token desde el archivo .env
    "POSTMARK_SERVER_TOKEN": config("POSTMARK_TOKEN", default=""),
}
# Lee el email por defecto desde el .env. Debe ser un email verificado en Postmark.
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@tuproyecto.com')
# Email para el formulario de contacto
EMAIL_CONTACTO = config('EMAIL_CONTACTO', default=DEFAULT_FROM_EMAIL)

EMAIL_USE_TLS = True