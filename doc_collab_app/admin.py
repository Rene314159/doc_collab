from django.contrib import admin
from .models import Document, DocumentVersion

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'updated_at', 'version')
    search_fields = ('title', 'owner__email')
    list_filter = ('created_at', 'updated_at')

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version', 'created_by', 'created_at')
    list_filter = ('created_at',)
