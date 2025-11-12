from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем Django settings для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

app = Celery('orders')

# Подгружаем настройки из Django (с префиксом CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находит tasks.py во всех установленных приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
