from django.contrib import admin

from .models import Document, DocumentType


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_required', 'order')
    list_editable = ('is_required', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_name', 'status', 'uploaded_at', 'reviewed_at')
    list_filter = ('status', 'document_type')
    list_editable = ('status',)
    search_fields = ('user__email', 'user__first_name', 'custom_name')
    readonly_fields = ('uploaded_at',)

    def get_name(self, obj):
        return obj.custom_name if obj.is_custom else (obj.document_type.name if obj.document_type else '—')
    get_name.short_description = 'Document'
