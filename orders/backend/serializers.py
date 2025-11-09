from django.db import transaction
from rest_framework import serializers
from models import ProductInfo, Order, Shop, Category, OrderItem


class CatalogShortSerializer(serializers.ModelSerializer):
    """
    Короткий формат каталога (для списка): минимальные поля для скорости.
    Возвращаем id (product_info id), название общего продукта, название магазина, цену и остаток.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = ProductInfo
        # id — это id записи ProductInfo
        fields = ('id', 'product_name', 'shop_name', 'price', 'quantity')


class ShopSerializer(serializers.ModelSerializer):
    """Простейший сериалайзер для Shop"""
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url')


class CategorySerializer(serializers.ModelSerializer):
    """Категории, если понадобятся в API"""
    class Meta:
        model = Category
        fields = ('id', 'name')


class OrderItemCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания позиции заказа.
    Клиент присылает product_info (id) и quantity.
    """
    product_info = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_info(self, value):
        try:
            pi = ProductInfo.objects.get(pk=value)
        except ProductInfo.DoesNotExist:
            raise serializers.ValidationError("ProductInfo с таким id не найден.")
        return value

    def validate(self, attrs):
        # Проверяем наличие достаточного количества
        pi = ProductInfo.objects.get(pk=attrs['product_info'])
        if attrs['quantity'] > pi.quantity:
            raise serializers.ValidationError(
                f"Недостаточно товара на складе. В наличии: {pi.quantity}"
            )
        return attrs


class OrderCreateSerializer(serializers.Serializer):
    """
    Создание заказа целиком: список items.
    Пример входа:
    {
       "items": [{"product_info": 12, "quantity": 3}, ...]
    }
    """
    items = OrderItemCreateSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        items = validated_data['items']

        with transaction.atomic():
            # Создаём заказ в статусе NEW (т.к. выбран минимальный сценарий)
            order = Order.objects.create(user=user, status=Order.Status.NEW)

            # Проходим по позициям, создаём OrderItem и уменьшаем остаток
            for it in items:
                pi = ProductInfo.objects.select_for_update().get(pk=it['product_info'])
                qty = it['quantity']

                # Повторная проверка (race conditions)
                if pi.quantity < qty:
                    raise serializers.ValidationError(
                        f"При сохранении обнаружилось, что товара недостаточно: {pi.id}"
                    )

                # Создаём OrderItem
                OrderItem.objects.create(order=order, product_info=pi, quantity=qty)

                # Уменьшаем остаток
                pi.quantity = pi.quantity - qty
                pi.save(update_fields=['quantity'])

        return order


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения позиции заказа"""
    product_name = serializers.CharField(source='product_info.product.name', read_only=True)
    shop_name = serializers.CharField(source='product_info.shop.name', read_only=True)
    price = serializers.FloatField(source='product_info.price', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'product_name', 'shop_name', 'price', 'quantity')


class OrderReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения заказа с его позициями"""
    items = OrderItemReadSerializer(many=True, read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'dt', 'status', 'items')