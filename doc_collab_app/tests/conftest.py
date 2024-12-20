# doc_collab_app/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from doc_collab_app.models import Document

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def collaborator():
    return User.objects.create_user(
        username='collaborator',
        email='collaborator@example.com',
        password='testpass123'
    )

@pytest.fixture
def document(user):
    return Document.objects.create(
        title='Test Document',
        content='Test Content',
        owner=user
    )

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
