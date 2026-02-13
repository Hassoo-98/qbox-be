from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'media_type', 'uploaded_by', 'file_size_human', 'created_at', 'is_active']
    list_filter = ['media_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'uploaded_by']
    readonly_fields = ['file_size', 'content_type', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def file_size_human(self, obj):
        """Display file size in human readable format"""
        if obj.file_size:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if obj.file_size < 1024.0:
                    return f"{obj.file_size:.2f} {unit}"
                obj.file_size /= 1024.0
            return f"{obj.file_size:.2f} TB"
        return 'N/A'
    
    file_size_human.short_description = 'File Size'
