

from pathlib import Path
from datetime import timedelta
from pathlib import Path
from django.conf import settings
import environ
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-fxl=8mkb+!#g*5$1ui-q781htt@$$l$rtimq8vl*6khm3_(uja'
DEBUG = True
APPEND_SLASH = False



ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".ngrok-free.app",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
    'drf_yasg'
]
AUTH_USER_MODEL = 'accounts.CustomUser'
MIDDLEWARE = [
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
        "rest_framework_simplejwt.authentication.JWTAuthentication",
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
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
     "USE_SESSION_AUTH": False,
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
    'DEFAULT_API_URL': '/',
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

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

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



STATIC_URL = 'static/'
