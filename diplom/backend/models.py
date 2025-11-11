from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Простой профиль для разделения ролей пользователя.
    - is_supplier: помечает пользователя как поставщика
    - shops: магазины, которыми управляет поставщик
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_supplier = models.BooleanField(default=False)
    # если пользователь — поставщик, он может быть связан с одним или несколькими Shop
    shops = models.ManyToManyField('Shop', blank=True, related_name='owners')

    def __str__(self):
        return f"{self.user.username} profile"
class Shop(models.Model):
    # Магазин/поставщик
    name = models.CharField(max_length=100)       # Название магазина/поставщика
    url = models.URLField(blank=True, null=True)  # URL для интеграции, может быть пустым

    def __str__(self):
        return self.name


class Category(models.Model):
    # Категория товара (например: Бытовая техника, Одежда и т.д.)
    name = models.CharField(max_length=100)
    shops = models.ManyToManyField(
        Shop,
        related_name='categories',
        blank=True
    )  # Категории, доступные у данного магазина

    def __str__(self):
        return self.name


class Product(models.Model):
    # Товар, без привязки к магазину
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
    )  # Категория товара

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    # Конкретная информация о товаре от конкретного магазина
    product = models.ForeignKey(
        Product,
        related_name='product_infos',
        on_delete=models.CASCADE
    )  # Ссылка на общий товар
    shop = models.ForeignKey(
        Shop,
        related_name='product_infos',
        on_delete=models.CASCADE
    )  # Магазин, у которого продаётся товар
    name = models.CharField(max_length=150)       # Название товара у магазина (может отличаться)
    quantity = models.PositiveIntegerField(default=0)  # Остаток товара в магазине
    price = models.FloatField()                   # Цена продажи
    price_rrc = models.FloatField()               # РРЦ — рекомендованная розничная цена

    class Meta:
        unique_together = ('product', 'shop')     # Уникальность: товар может быть один раз у магазина

    def __str__(self):
        return f"{self.product.name} ({self.shop.name})"


class Parameter(models.Model):
    # Дополнительные параметры товара (например: цвет, размер, бренд)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    # Значение параметра для конкретного ProductInfo
    product_info = models.ForeignKey(
        ProductInfo,
        related_name='parameters',
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter,
        related_name='product_parameters',
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=100)  # Значение параметра (например: "красный", "42", "Lenovo")

    class Meta:
        unique_together = ('product_info', 'parameter')  # Один параметр = одно значение для товара

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


class Order(models.Model):
    # Заказ пользователя

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"           # Пользователь ещё не завершил заказ
        NEW = "new", "Новый"                  # Заказ отправлен, но ещё не подтверждён
        CONFIRMED = "confirmed", "Подтверждён" # Принят поставщиком/админом
        SHIPPED = "shipped", "Отгружен"       # Отправлен пользователю
        DELIVERED = "delivered", "Доставлен"  # Получен пользователем
        CANCELED = "canceled", "Отменён"      # Заказ отменён

    user = models.ForeignKey(
        User,
        related_name='diplom',
        on_delete=models.CASCADE
    )  # Пользователь, оформивший заказ
    dt = models.DateTimeField(auto_now_add=True)  # Дата и время создания заказа
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )  # Текущий статус заказа

    def __str__(self):
        return f"Order {self.id} ({self.user.username})"


class OrderItem(models.Model):
    # Позиция заказа — конкретный товар от конкретного магазина
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )  # Ссылка на заказ
    product_info = models.ForeignKey(
        ProductInfo,
        related_name='order_items',
        on_delete=models.CASCADE
    )  # Ссылка на товар у конкретного магазина
    quantity = models.PositiveIntegerField(default=1)  # Количество товара

    class Meta:
        unique_together = ('order', 'product_info')  # Нельзя добавить один и тот же товар дважды

    def __str__(self):
        return f"{self.product_info} x {self.quantity}"


class Contact(models.Model):
    # Контактная информация пользователя (телефон, email, адрес)
    class ContactType(models.TextChoices):
        PHONE = 'phone', 'Телефон'
        EMAIL = 'email', 'Email'
        ADDRESS = 'address', 'Адрес'

    user = models.ForeignKey(
        User,
        related_name='contacts',
        on_delete=models.CASCADE
    )  # Пользователь, которому принадлежит контакт
    type = models.CharField(
        max_length=20,
        choices=ContactType.choices
    )  # Тип контакта
    value = models.CharField(max_length=100)  # Значение контакта (номер, email, адрес)

    def __str__(self):
        return f"{self.user.username} {self.type}: {self.value}"
