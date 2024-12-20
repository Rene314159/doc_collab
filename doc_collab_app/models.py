from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.JSONField(default=dict)  # Store document content as JSON for rich text
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_documents')
    version = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.title

    def has_user_permission(self, user, required_level='view'):
        if self.owner == user:
            return True
            
        try:
            permission = self.documentpermission_set.get(user=user)
            if required_level == 'view':
                return True
            elif required_level == 'edit':
                return permission.permission_level in ['edit', 'admin']
            elif required_level == 'admin':
                return permission.permission_level == 'admin'
        except DocumentPermission.DoesNotExist:
            return False
        
        return False

    class Meta:
        ordering = ['-updated_at']

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    content = models.JSONField()
    version = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    operation_type = models.CharField(max_length=20)  # insert, delete, format
    operation_data = models.JSONField()  # Store operation details


    
    class Meta:
        ordering = ['-version']
        unique_together = ['document', 'version']

    
    
class DocumentPermission(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'Can Edit'),
        ('admin', 'Admin Access')
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='granted_permissions'
    )

    class Meta:
        unique_together = ['document', 'user']

