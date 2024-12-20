# doc_collab_app/tests/test_websockets.py
import pytest
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from doc_collab_app.consumers import DocumentConsumer

@pytest.mark.asyncio
@pytest.mark.django_db
class TestWebSocket:
    async def test_document_consumer(self, document, user):
        # Create an application with the routing
        application = URLRouter([
            re_path(r"ws/document/(?P<document_id>[\w-]+)/$", DocumentConsumer.as_asgi()),
        ])
        
        communicator = WebsocketCommunicator(
            application,
            f"/ws/document/{document.id}/"
        )
        # Set the user in the scope
        communicator.scope["user"] = user

        connected, _ = await communicator.connect()
        assert connected

        try:
            await communicator.send_json_to({
                'type': 'document_update',
                'data': {'content': 'Updated content'},
                'version': 1
            })

            response = await communicator.receive_json_from()
            assert response['type'] == 'document_update'
        finally:
            await communicator.disconnect()
