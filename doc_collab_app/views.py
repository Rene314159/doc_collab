from rest_framework import viewsets, status
# from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, DocumentVersion, DocumentPermission
from .serializers import DocumentSerializer, DocumentVersionSerializer

# Define User at module level
# User = get_user_model()

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
        """Invite a collaborator to a document"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        document = self.get_object()
        user_email = request.data.get('user_email')
        permission_level = request.data.get('permission_level')
        
        if not user_email or not permission_level:
            return Response(
                {'error': 'Both user_email and permission_level are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if permission_level not in ['view', 'edit', 'admin']:
            return Response(
                {'error': 'Invalid permission level'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_to_invite = User.objects.get(email=user_email)
            # Check if permission already exists
            permission, created = DocumentPermission.objects.get_or_create(
                document=document,
                user=user_to_invite,
                defaults={'permission_level': permission_level, 'created_by': request.user}
            )
            
            if not created:
                permission.permission_level = permission_level
                permission.save()
            
            return Response({
                'status': 'user invited',
                'user_email': user_email,
                'permission_level': permission_level
            })
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
        
        if not user_email:
            return Response(
                {'error': 'user_email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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
        
        if not user_email or not new_permission_level:
            return Response(
                {'error': 'Both user_email and permission_level are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_permission_level not in ['view', 'edit', 'admin']:
            return Response(
                {'error': 'Invalid permission level'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            permission = DocumentPermission.objects.get(
                document=document,
                user__email=user_email
            )
            permission.permission_level = new_permission_level
            permission.save()
            return Response({
                'status': 'permission updated',
                'user_email': user_email,
                'permission_level': new_permission_level
            })
        except DocumentPermission.DoesNotExist:
            return Response(
                {'error': 'Permission not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
