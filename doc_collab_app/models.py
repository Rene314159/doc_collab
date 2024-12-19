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
    