import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from decouple import config


# 1. Carga variables de entorno desde .env
load_dotenv()  # debe ir lo antes posible

# 2. Paths base
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Seguridad
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 4. Apps instaladas
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tu app
    'gestion_activos',

    # allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    "anymail",
]

SITE_ID = 1

# 5. Middleware (con WhiteNoise para estáticos)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',           #  ← WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'inventario.urls'

# 6. Templates (global + app dirs)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],  # tu carpeta global
        'APP_DIRS': True,
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

# 7. Base de datos (puedes cambiar a Postgres en producción)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('postgresql://inventario_cantv_db_user:78W0okyU6o5WWTgrrHFxq7iZKSmBhe5N@dpg-d0qj2s3uibrs73el76p0-a/inventario_cantv_db'),
        conn_max_age=600,  # mantiene la conexión abierta
        ssl_require=True   # importante para Render
    )
}

# 8. Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# 9. Autenticación con allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 10. Internacionalización
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 11. Archivos estáticos y media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'        # para collectstatic
STATICFILES_DIRS = [BASE_DIR / 'gestion_activos' / 'static'] # tu CSS/JS local
# activa compresión de WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 12. Login / logout / redirecciones
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'lista_activos'
LOGOUT_REDIRECT_URL = 'login'

# 13. Variables extra de allauth (opcional)
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']
# --- Seguridad base de datos ---
DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# settings.py
EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": config("POSTMARK_TOKEN")
}
DEFAULT_FROM_EMAIL = "noreply@tudominio.com"  # Debe estar verificado en Postmark
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'no-reply@inventario.com'