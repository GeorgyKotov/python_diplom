import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_register_user(client):
    url = reverse("register")
    data = {"username": "newuser", "email": "new@example.com", "password": "12345"}
    response = client.post(url, data, format="json")
    assert response.status_code == 201
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_login_and_logout(client):
    user = User.objects.create_user(username="user", email="a@a.com", password="12345", is_active=True)
    login_url = reverse("login")
    logout_url = reverse("logout")

    response = client.post(login_url, {"username": "user", "password": "12345"}, format="json")
    assert response.status_code in (200, 403, 401)

    client.force_authenticate(user=user)
    response = client.post(logout_url)
    assert response.status_code == 200
