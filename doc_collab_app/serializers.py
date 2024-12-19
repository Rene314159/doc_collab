# doc_collab_app/serializers.py
from rest_framework import serializers
from .models import Document, DocumentVersion

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'version', 'created_at', 'updated_at']
        read_only_fields = ['version', 'created_at', 'updated_at']

class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ['id', 'document', 'content', 'version', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'created_by']
