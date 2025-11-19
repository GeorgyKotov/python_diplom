from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+_bjhw$d+ezo2!s14ynbv#)1v)0j#qnyy-dh)y1y(qb3=3r2-0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend',
    'rest_framework',
    'corsheaders',
    'easy_thumbnails',
    'cachalot',
    'drf_spectacular',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'orders.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'orders.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    ]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Письма выводим в консоль, чтобы не настраивать почту на этапе разработки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGIN_URL = '/login'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "100/minute",
    },
    "DEFAULT_THROTTLE_CACHE": "throttle",
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Online Shop API",
    "DESCRIPTION": "Документация к API интернет-магазина (заказы, пользователи, контакты и т.д.)",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# Настройки Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "GOOGLE_CLIENT_ID"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "GOOGLE_CLIENT_SECRET"

SOCIAL_AUTH_GITHUB_KEY = "GITHUB_CLIENT_ID"
SOCIAL_AUTH_GITHUB_SECRET = "GITHUB_CLIENT_SECRET"

LOGIN_URL = "login/"
LOGIN_REDIRECT_URL = "home/"
LOGOUT_REDIRECT_URL = "login/"

SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/logged-in/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/profile-setup/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/settings/'


CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

JAZZMIN_SETTINGS = {
    "site_title": "Kotov Shop Admin",
    "site_header": "Админ-панель Kotov Shop",
    "site_brand": "Kotov Shop",
    "welcome_sign": "Добро пожаловать в панель управления",
    "copyright": "© 2025 Kotov Technologies",
    "search_model": ["backend.Product", "backend.Category"],

    "topmenu_links": [
        {"name": "Главная", "url": "admin:index", "icon": "fas fa-home"},
        {"name": "GitHub проекта", "url": "https://github.com/GeorgyKotov/python_diplom", "new_window": True},
    ],

    "show_sidebar": True,
    "navigation_expanded": False,

    "icons": {
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "backend.Category": "fas fa-folder",
        "backend.Product": "fas fa-box",
    },

    "custom_css": None,
    "custom_js": None,
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,

    "navbar": "navbar-dark bg-primary",
    "accent": "accent-primary",
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

THUMBNAIL_ALIASES = {
    '': {
        'avatar_small': {'size': (50, 50), 'crop': True},
        'avatar_medium': {'size': (200, 200), 'crop': True},
        'product_small': {'size': (150, 150), 'crop': True},
        'product_medium': {'size': (600, 600), 'crop': True},
    }
}

THUMBNAIL_DEFAULT_STORAGE = 'django.core.files.storage.FileSystemStorage'


sentry_sdk.init(
    dsn="https://5789954a5b6b4a3e151e99348a08231e@o4510387547275264.ingest.de.sentry.io/4510387552518224",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "TIMEOUT": None, 
    }
}

CACHALOT_ENABLED = True
CACHALOT_CACHE = 'default'
CACHALOT_TIMEOUT = None



