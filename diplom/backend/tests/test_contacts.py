import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from backend.models import Contact


@pytest.fixture
def auth_client(db):
    client = APIClient()
    user = User.objects.create_user(username="client1", email="client1@mail.com", password="testpass", is_active=True)
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_add_contact(auth_client):
    client, _ = auth_client
    url = reverse("contacts")
    data = {"type": "address", "value": "Moscow, Tverskaya 1"}
    response = client.post(url, data, format="json")
    assert response.status_code == 201
    assert "id" in response.data


@pytest.mark.django_db
def test_get_contacts(auth_client):
    client, user = auth_client
    Contact.objects.create(user=user, type="phone", value="+79990001122")
    url = reverse("contacts")
    response = client.get(url)
    assert response.status_code == 200
    assert "contacts" in response.data
