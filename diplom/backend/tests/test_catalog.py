import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from backend.models import ProductInfo, Product,Category, Shop


@pytest.mark.django_db
def test_catalog_list():
    client = APIClient()
    category = Category.objects.create(name="Electronics")
    shop = Shop.objects.create(name="Tech Store")
    product = Product.objects.create(name="Laptop", category=category)
    ProductInfo.objects.create(product=product, name="Laptop", price=1000, quantity=3, shop=shop, price_rrc=1200)
    url = reverse("catalog")
    response = client.get(url)
    assert response.status_code == 200
    assert "items" in response.data
