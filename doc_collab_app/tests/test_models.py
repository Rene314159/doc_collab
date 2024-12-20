# doc_collab_app/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model
from doc_collab_app.models import Document, DocumentPermission

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def document(user):
    return Document.objects.create(
        title='Test Document',
        content='Test Content',
        owner=user
    )

@pytest.mark.django_db
class TestDocument:
    def test_document_creation(self, document, user):
        assert document.title == 'Test Document'
        assert document.content == 'Test Content'
        assert document.owner == user
        assert document.version == 1

    def test_document_str(self, document):
        assert str(document) == 'Test Document'

@pytest.fixture
def collaborator():
    return User.objects.create_user(
        username='collaborator',
        email='collaborator@example.com',
        password='testpass123'
    )

@pytest.mark.django_db
class TestDocumentPermission:
    def test_permission_creation(self, document, collaborator, user):
        permission = DocumentPermission.objects.create(
            document=document,
            user=collaborator,
            permission_level='edit',
            created_by=user
        )
        assert permission.permission_level == 'edit'
        assert permission.user == collaborator
