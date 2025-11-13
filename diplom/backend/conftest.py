import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_celery_tasks():
    with patch("backend.views.send_registration_confirmation_email.delay", lambda *a, **k: None), \
            patch("backend.views.send_order_confirmation_email.delay", lambda *a, **k: None):
        yield
