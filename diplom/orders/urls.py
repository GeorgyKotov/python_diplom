from django.contrib import admin
from django.urls import path, include
from backend.views import (
    RegisterAPIView,
    ConfirmAPIView,
    LoginAPIView,
    LogoutAPIView,
    CatalogAPIView,
    CartAPIView,
    ContactsAPIView,
    ContactDetailAPIView,
    OrderCreateAPIView,
    OrdersListAPIView,
    home,
    TriggerErrorAPIView
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Стандартная админка Django (для проверки данных)
    path('admin/', admin.site.urls),
    # Регистрация и подтверждение аккаунта
    # POST — регистрация, создаёт пользователя и отправляет письмо
    path('register/', RegisterAPIView.as_view(), name='register'),
    # GET — переходим по ссылке из email, чтобы активировать аккаунт
    path('confirm/', ConfirmAPIView.as_view(), name='confirm'),

    # Авторизация пользователя
    # POST — вход (создаёт сессию)
    path('login/', LoginAPIView.as_view(), name='login'),
    # POST — выход (удаляет сессию)
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    # Каталог товаров
    # GET — получить список товаров
    path('catalog/', CatalogAPIView.as_view(), name='catalog'),

    # Корзина
    # GET — получить корзину
    # POST — добавить товар в корзину
    # DELETE — удалить товар из корзины
    path('cart/', CartAPIView.as_view(), name='cart'),

    # Контакты (адреса доставки)
    # GET — список контактов
    # POST — создать контакт
    path('contacts/', ContactsAPIView.as_view(), name='contacts'),
    # GET/DELETE — работа с определённым контактом по ID
    path('contacts/<int:pk>/', ContactDetailAPIView.as_view(), name='contact_detail'),

    # Заказы
    # POST — создать заказ (из корзины или переданных товаров)
    path('orders/create/', OrderCreateAPIView.as_view(), name='order_create'),
    # GET — список заказов пользователя
    path('orders/', OrdersListAPIView.as_view(), name='orders_list'),

    # Автоматическая генерация документации DRF-Spectacular
    path("schema/", SpectacularAPIView.as_view(), name="schema"),  
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Авторизация через социальные сети
    path('auth/', include('social_django.urls', namespace='social')),
    path('', home, name='home'),

    path("debug/sentry/", TriggerErrorAPIView.as_view()),
]
