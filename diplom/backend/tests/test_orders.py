import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.conf import settings
from backend.models import Contact, ProductInfo, Order, Product,Category, Shop


@pytest.fixture
def auth_client(db):
    client = APIClient()
    user = User.objects.create_user(username="buyer", email="buyer@mail.com", password="testpass", is_active=True)
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_create_order(auth_client):
    client, user = auth_client
    category = Category.objects.create(name="Phones")
    shop = Shop.objects.create(name="Tech Store")
    product = Product.objects.create(name="Phone", category=category)
    product_info = ProductInfo.objects.create(
        product=product,
        name="Phone",
        price=500,
        quantity=10,
        shop=shop,
        price_rrc=1200
    )

    contact = Contact.objects.create(user=user, type="address", value="Moscow")

    session = client.session
    session["cart"] = {str(product_info.id): 2}
    session.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    url = reverse("order_create")
    response = client.post(url, {"contact_id": contact.id}, format="json")

    print(response.data)
    assert response.status_code in (200, 201)
    assert "order_id" in response.data
    assert Order.objects.filter(user=user).exists()