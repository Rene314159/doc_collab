from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .operations import transform_operation, apply_operation
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
import json

class DocumentConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'document_{self.document_id}'

        # Verify user has permission
        if not await self.has_permission():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send current document state
        await self.send_document_state()

    @database_sync_to_async
    def has_permission(self):
        try:
            document = Document.objects.get(id=self.document_id)
            return document.has_user_permission(self.scope['user'])
        except ObjectDoesNotExist:
            return False

    async def receive_json(self, content):
        operation_type = content.get('type')
        operation_data = content.get('data')
        version = content.get('version')

        if not all([operation_type, operation_data, version]):
            return

        # Transform operation against any concurrent operations
        transformed_op = await self.transform_operation(operation_type, operation_data, version)
        if not transformed_op:
            # Send current state if operation cannot be transformed
            await self.send_document_state()
            return

        # Apply operation to document
        success = await self.apply_operation(transformed_op)
        if success:
            # Broadcast to other clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'document_operation',
                    'operation': transformed_op,
                    'user_id': self.scope['user'].id
                }
            )

    @database_sync_to_async
    def transform_operation(self, op_type, op_data, version):
        document = Document.objects.select_for_update().get(id=self.document_id)
        if document.version > version:
            # Transform operation against all operations since client version
            concurrent_ops = document.versions.filter(version__gt=version).order_by('version')
            transformed = op_data
            for concurrent in concurrent_ops:
                transformed = transform_operation(transformed, concurrent.operation_data)
            return {
                'type': op_type,
                'data': transformed,
                'version': document.version + 1
            }
        return None

    @database_sync_to_async
    def apply_operation(self, operation):
        try:
            with transaction.atomic():
                document = Document.objects.select_for_update().get(id=self.document_id)
                
                # Apply operation to document content
                document.content = apply_operation(document.content, operation['data'])
                document.version += 1
                document.save()

                # Create version record
                DocumentVersion.objects.create(
                    document=document,
                    content=document.content,
                    version=document.version,
                    created_by=self.scope['user'],
                    operation_type=operation['type'],
                    operation_data=operation['data']
                )
                return True
        except Exception as e:
            print(f"Error applying operation: {e}")
            return False
