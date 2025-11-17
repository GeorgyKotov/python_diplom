from django.contrib import admin
from .models import (
    Profile, Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Order, OrderItem, Contact
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_supplier")
    list_filter = ("is_supplier",)
    search_fields = ("user__username",)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url")
    search_fields = ("name",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)
    filter_horizontal = ("shops",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    search_fields = ("name",)

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "shop", "price", "price_rrc", "quantity")
    search_fields = ("name",)
    list_filter = ("shop", "product")

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ("id", "product_info", "parameter", "value")
    list_filter = ("parameter",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "dt")
    search_fields = ("user__username",)
    list_filter = ("status",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_info", "quantity", "price")
    list_filter = ("order",)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "value")
    list_filter = ("type",)
    search_fields = ("user__username",)
