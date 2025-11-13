import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from backend.models import User

@pytest.fixture(autouse=True)
def mock_celery_tasks():
    with patch("backend.views.send_registration_confirmation_email.delay", lambda *a, **k: None), \
            patch("backend.views.send_order_confirmation_email.delay", lambda *a, **k: None):
        yield


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(
        username="buyer",
        password="12345",
        email="buyer@example.com"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user