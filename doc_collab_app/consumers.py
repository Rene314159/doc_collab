from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
# from .models import Document
import base64
import logging

logger = logging.getLogger(__name__)

class DocumentConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        #from .models import Document
        print("="*50)  # Very visible separator
        print("CONNECT METHOD STARTED")
        print(f"SCOPE: {self.scope}")
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        print(f"DOCUMENT ID: {self.document_id}")
        self.room_group_name = f'document_{self.document_id}'
        self.authenticated = False
        print("ABOUT TO ACCEPT CONNECTION")
        await self.accept()
        print("CONNECTION ACCEPTED")
        print("="*50)

    async def disconnect(self, close_code):
        print(f"Disconnecting with code: {close_code}")  # Debug print
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        print("Disconnected from group")  # Debug print

    async def receive_json(self, content):
        print(f"Received message: {content}")  # Debug print
        if not self.authenticated:
            await self.handle_authentication(content)
            return

        message_type = content.get('type')
        if message_type == 'document_update':
            await self.handle_document_update(content)

    async def handle_authentication(self, content):
        print("Handling authentication...")  # Debug print
        if content.get('type') != 'authenticate':
            print("Not an authentication message, closing")  # Debug print
            await self.close()
            return

        auth_token = content.get('token', '')
        try:
            username, password = base64.b64decode(auth_token).decode('utf-8').split(':', 1)
            print(f"Attempting to authenticate user: {username}")  # Debug print
            if await self.authenticate_user(username, password):
                print("User authenticated, checking permissions")  # Debug print
                if await self.has_permission('edit'):
                    print("User has edit permission")  # Debug print
                    await self.complete_authentication()
                else:
                    print(f"Permission denied for user {username}")  # Debug print
                    await self.close()
            else:
                print(f"Authentication failed for user {username}")  # Debug print
                await self.close()
        except Exception as e:
            print(f"Authentication error: {str(e)}")  # Debug print
            await self.close()

    async def complete_authentication(self):
        print("Completing authentication process...")  # Debug print
        self.authenticated = True
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.send_json({
            'type': 'authentication_successful'
        })
        print(f"Authentication completed, joined group: {self.room_group_name}")  # Debug print

    async def handle_document_update(self, content):
        print(f"Handling document update: {content}")  # Debug print
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_update',
                    'content': content.get('data'),
                    'version': content.get('version'),
                    'user_id': self.scope['user'].id
                }
            )
            print("Update broadcasted successfully")  # Debug print
        except Exception as e:
            print(f"Error broadcasting update: {str(e)}")  # Debug print
            await self.send_json({
                'type': 'error',
                'message': 'Failed to broadcast update'
            })

    async def broadcast_update(self, event):
        print(f"Broadcasting update: {event}")  # Debug print
        await self.send_json({
            'type': 'document_update',
            'content': event['content'],
            'version': event['version'],
            'user_id': event['user_id']
        })

    @database_sync_to_async
    def authenticate_user(self, username, password):
        print(f"Database: Authenticating user {username}")  # Debug print
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                print(f"Database: User {username} authenticated successfully")  # Debug print
                self.scope['user'] = user
                return True
            print(f"Database: Invalid password for user {username}")  # Debug print
        except User.DoesNotExist:
            print(f"Database: User {username} not found")  # Debug print
        return False

    @database_sync_to_async
    def has_permission(self, required_level):
        from .models import Document
        print(f"Database: Checking {required_level} permission for document {self.document_id}")  # Debug print
        try:
            document = Document.objects.get(id=self.document_id)
            has_perm = document.has_user_permission(self.scope['user'], required_level)
            print(f"Database: Permission check result: {has_perm}")  # Debug print
            return has_perm
        except Document.DoesNotExist:
            print(f"Database: Document {self.document_id} not found")  # Debug print
            return False
        
