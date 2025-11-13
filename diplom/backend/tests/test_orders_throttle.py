import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_order_list_throttling(auth_client):
    client, user = auth_client
    client.force_authenticate(user=user)
    url = reverse("orders_list")

    # Сначала 1 запрос должен пройти успешно
    response = client.get(url)
    assert response.status_code in (200, 204)

    # Теперь превысим лимит
    for _ in range(200):
        response = client.get(url)

    # Проверяем, что после лимита приходит 429
    assert response.status_code == 429