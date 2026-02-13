

from pathlib import Path
from datetime import timedelta
from pathlib import Path
from django.conf import settings
import environ
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-fxl=8mkb+!#g*5$1ui-q781htt@$$l$rtimq8vl*6khm3_(uja'
DEBUG = True
APPEND_SLASH = False

CROSS_ALLOW_CREDENTIALS=True
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".ngrok-free.app",
    "backend.qbox.sa"
]
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "http://localhost:5173",
    "http://backend.qbox.sa"
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"}
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.request": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}



# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1",
    "https://.ngrok-free.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
      "http://backend.qbox.sa"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.ngrok-free\.app$",
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
    'rest_framework',
    'django_filters',
    'accounts',
    'driver',
    "staff",
    "home_owner",
    "q_box",
    "packages",
    "service_provider",
    "locations", 
    'drf_yasg',
    'package_timeline',
    "promotion"

]
AUTH_USER_MODEL = 'accounts.CustomUser'
SESSION_COOKIE_SAMESITE = None
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES":[
        "core.authentication.CookieJWTAuthentication",
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Swagger/OpenAPI Settings
SWAGGER_SETTINGS = {
  'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
     "USE_SESSION_AUTH": False,
  'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
       'DEFAULT_API_URL': 'https://backend.qbox.sa/',
    'OPERATIONS_SORTER': 'method',
    'TAGS_SORTER': 'alpha',
    'APIS_SORTER': 'alpha',
    'TITLE': 'Qbox API',
    'DESCRIPTION': 'Qbox Backend API Documentation',
    'VERSION': 'v1',
    'SHOW_REQUEST_HEADERS': True,
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'patch', 'delete'],
    'VALIDATOR_URL': '',
}

REDOC_SETTINGS = {
    'TITLE': 'Qbox API',
    'DESCRIPTION': 'Qbox Backend API Documentation',
    'VERSION': 'v1',
    'SPEC_URL': '/swagger/schema/',
    'DEFAULT_API_URL': '/',
}

# Schema URL for drf_yasg
# SCHEMA_URL = 'http://backend.qbox.sa'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
      'AUTH_COOKIE': 'access_token',
    'AUTH_COOKIE_SECURE': True,
    'AUTH_COOKIE_HTTPONLY': True,
    'AUTH_COOKIE_SAMESITE': 'none',  # Change from 'strict' to 'none'
    'AUTH_COOKIE_DOMAIN': 'backend.qbox.sa',
}
FORCE_SCRIPT_NAME = '/api'

ROOT_URLCONF = 'core.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
WSGI_APPLICATION = 'core.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qbox_db',
        'USER': 'qbox_user',
        'PASSWORD': 'strongpassword123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)
    print(f"Loaded .env from: {env_file}")    
else:
    print(f"WARNING: .env file not found at {env_file}")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = env('EMAIL_HOST', default='sandbox.smtp.mailtrap.io')
EMAIL_PORT = env.int('EMAIL_PORT', default=2525)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)


MAILTRAP_TOKEN = env('MAILTRAP_TOKEN', default='')

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Media files (QR codes, images, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    '/home/hassaanqazi/Documents/qbox-be/venv/lib/python3.14/site-packages/drf_yasg/static',
]
