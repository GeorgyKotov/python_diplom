from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import ProductInfo, Contact

# Получаем модель пользователя (стандартная User или кастомная, если настроена)
User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Сериализатор для регистрации.
    Проверяет, что пользователь прислал имя, email и пароль.
    Пока без сложной валидации — только проверка наличия.
    """
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа в систему.
    Проверяем только наличие полей логина и пароля.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода товаров (ProductInfo).
    Показываем клиенту основные данные: какой товар, какой магазин, цена и остаток.
    """
    # Преобразуем связанные поля в строку для удобного отображения
    product = serializers.CharField(source='product.__str__', read_only=True)
    shop = serializers.CharField(source='shop.__str__', read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'shop', 'price', 'quantity')


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода и создания контактов пользователя.
    Контакт — это адрес или телефон, куда доставим заказ.
    """
    class Meta:
        model = Contact
        fields = ('id', 'type', 'value')
        read_only_fields = ('id',)