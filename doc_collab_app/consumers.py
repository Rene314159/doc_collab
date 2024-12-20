# doc_collab_app/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import AcceptConnection, DenyConnection, StopConsumer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
import json
import logging

logger = logging.getLogger(__name__)


class DocumentConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Get auth header from scope
        headers = dict(self.scope['headers'])
        if b'authorization' in headers:
            try:
                # Parse basic auth
                auth_header = headers[b'authorization'].decode('utf-8')
                auth_type, auth_data = auth_header.split(' ', 1)
                if auth_type.lower() == 'basic':
                    username, password = base64.b64decode(auth_data).decode('utf-8').split(':', 1)
                    # Verify credentials
                    if await self.authenticate_user(username, password):
                        await self.accept()
                        self.document_id = self.scope['url_route']['kwargs']['document_id']
                        self.room_group_name = f'document_{self.document_id}'
                        await self.channel_layer.group_add(
                            self.room_group_name,
                            self.channel_name
                        )
                        return
            except Exception as e:
                print(f"Authentication error: {e}")
        
        # If we get here, authentication failed
        await self.close()

    @database_sync_to_async
    def authenticate_user(self, username, password):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                self.scope['user'] = user
                return True
        except User.DoesNotExist:
            pass
        return False

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive_json(self, content):
        try:
            message_type = content.get('type')
            if message_type == 'document_update':
                await self.handle_document_update(content)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self.send_json({
                'type': 'error',
                'message': 'Internal server error'
            })

    @database_sync_to_async
    def check_document_access(self):
        from .models import Document
        document = Document.objects.get(id=self.document_id)
        return document.has_user_access(self.scope['user'])

    @database_sync_to_async
    def save_document_update(self, content):
        from .models import Document, DocumentVersion
        document = Document.objects.select_for_update().get(id=self.document_id)
        
        # Create new version
        DocumentVersion.objects.create(
            document=document,
            content=document.content,
            version=document.version,
            created_by=self.scope['user']
        )
        
        # Update document
        document.content = content
        document.version += 1
        document.save()
        
        return document.version

    async def handle_document_update(self, content):
        try:
            new_version = await self.save_document_update(content['data'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_update',
                    'content': content['data'],
                    'version': new_version,
                    'user_id': self.scope['user'].id
                }
            )
        except Exception as e:
            logger.error(f"Error saving document update: {str(e)}")
            await self.send_json({
                'type': 'error',
                'message': 'Failed to save document'
            })

    async def broadcast_update(self, event):
        await self.send_json({
            'type': 'document_update',
            'content': event['content'],
            'version': event['version'],
            'user_id': event['user_id']
        })
