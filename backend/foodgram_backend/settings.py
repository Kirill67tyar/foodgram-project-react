import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(j5tdm_euxl=c@@!)!wi%d$cb%85&qz9j+(fmet&f*%3gqor2g'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_extensions',
    'debug_toolbar',
    'corsheaders',
    'django_filters',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'orders.apps.OrdersConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram_backend.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

AUTH_USER_MODEL = 'users.User'
# AUTH_USER_MODEL = 'users.models.User'

LANGUAGE_CODE = 'ru-RU'  # 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
# STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    'HIDE_USERS': False,
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        # 'user': 'api.serializers.UserModelSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        # 'activation': ['rest_framework.permissions.AllowAny'],
        # 'password_reset': ['rest_framework.permissions.AllowAny'],
        # 'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
        # 'set_password': ['djoser.permissions.CurrentUserOrAdmin'],
        # 'username_reset': ['rest_framework.permissions.AllowAny'],
        # 'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
        # 'set_username': ['djoser.permissions.CurrentUserOrAdmin'],
        # 'user_create': ['rest_framework.permissions.AllowAny'],
        # 'user_delete': ['djoser.permissions.CurrentUserOrAdmin'],
        'user': ['djoser.permissions.CurrentUserOrAdmin'],
        # 'token_create': ['rest_framework.permissions.AllowAny'],
        # 'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    },
    # 'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    # 'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    # 'ACTIVATION_URL': '#/activate/{uid}/{token}',
    # 'SEND_ACTIVATION_EMAIL': True,
    # 'SERIALIZERS': {},

}
INTERNAL_IPS = ['127.0.0.1',]

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'
