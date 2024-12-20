# doc_collab_app/tests/test_views.py
import pytest
from rest_framework import status
from doc_collab_app.models import Document, DocumentPermission

@pytest.mark.django_db
class TestDocumentViewSet:
    def test_create_document(self, authenticated_client):
        data = {
            'title': 'New Document',
            'content': 'New Content'
        }
        response = authenticated_client.post('/api/documents/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Document.objects.count() == 1

    def test_invite_collaborator(self, authenticated_client, document, collaborator):
        data = {
            'user_email': 'collaborator@example.com',
            'permission_level': 'edit'
        }
        response = authenticated_client.post(
            f'/api/documents/{document.id}/invite/',
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
