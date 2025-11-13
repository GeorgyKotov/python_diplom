import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_order_list_throttling(auth_client):
    client, user = auth_client
    client.force_authenticate(user=user)
    url = reverse("orders_list")  # имя маршрута для OrdersListAPIView

    for _ in range(1000):
        response = client.get(url)
        assert response.status_code in (200, 204)

    # 1001-й должен вернуть 429 (Too Many Requests)
    response = client.get(url)
    assert response.status_code == 429