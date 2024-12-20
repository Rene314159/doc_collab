from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, DocumentVersion
from .serializers import DocumentSerializer, DocumentVersionSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        document = self.get_object()
        versions = DocumentVersion.objects.filter(document=document)
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        document = self.get_object()
        user_email = request.data.get('user_email')
        permission_level = request.data.get('permission_level')
        
        try:
            user_to_invite = User.objects.get(email=user_email)
            DocumentPermission.objects.create(
                document=document,
                user=user_to_invite,
                permission_level=permission_level,
                created_by=request.user
            )
            return Response({'status': 'user invited'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def revoke_access(self, request, pk=None):
        document = self.get_object()
        user_email = request.data.get('user_email')
        
        try:
            permission = DocumentPermission.objects.get(
                document=document,
                user__email=user_email
            )
            permission.delete()
            return Response({'status': 'access revoked'})
        except DocumentPermission.DoesNotExist:
            return Response(
                {'error': 'Permission not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite a collaborator to a document"""
        document = self.get_object()
        user_email = request.data.get('user_email')
        permission_level = request.data.get('permission_level')
        
        try:
            user_to_invite = User.objects.get(email=user_email)
            DocumentPermission.objects.create(
                document=document,
                user=user_to_invite,
                permission_level=permission_level,
                created_by=request.user
            )
            return Response({'status': 'user invited'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def revoke_access(self, request, pk=None):
        """Revoke a collaborator's access"""
        document = self.get_object()
        user_email = request.data.get('user_email')
        
        try:
            permission = DocumentPermission.objects.get(
                document=document,
                user__email=user_email
            )
            permission.delete()
            return Response({'status': 'access revoked'})
        except DocumentPermission.DoesNotExist:
            return Response(
                {'error': 'Permission not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def update_permission(self, request, pk=None):
        """Update a collaborator's permission level"""
        document = self.get_object()
        user_email = request.data.get('user_email')
        new_permission_level = request.data.get('permission_level')
        
        try:
            permission = DocumentPermission.objects.get(
                document=document,
                user__email=user_email
            )
            permission.permission_level = new_permission_level
            permission.save()
            return Response({'status': 'permission updated'})
        except DocumentPermission.DoesNotExist:
            return Response(
                {'error': 'Permission not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )




