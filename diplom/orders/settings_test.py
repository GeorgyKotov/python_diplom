from .settings import *

# -----------------------------
# ТЕСТОВАЯ БАЗА ДАННЫХ (in-memory)
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# -----------------------------
# ОТКЛЮЧАЕМ REDIS ПОЛНОСТЬЮ
# -----------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'testing-default',
    },
    'throttle': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'testing-throttle',
    }
}

# Cachalot отключаем — он мешает миграциям во время тестов
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'cachalot']

CACHALOT_ENABLED = False

# -----------------------------
# CELERY в фейковом режиме
# -----------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# -----------------------------
# EMAIL backend — в память
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# -----------------------------
# SENTRY отключить
# -----------------------------
SENTRY_DSN = None

# DRF throttle storage не должен лезть в redis
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = [
    "rest_framework.throttling.UserRateThrottle",
]

REST_FRAMEWORK["DEFAULT_THROTTLE_CACHE"] = "throttle"

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "user": "20/minute",  # лимит для теста
    "anon": "1000/minute",  # просто чтобы не мешал
}
# -----------------------------
# Медиа — в /tmp
# -----------------------------
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()
