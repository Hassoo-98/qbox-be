from rest_framework import serializers
from drf_yasg import openapi
from .models import Media


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for Media CRUD operations"""
    
    file_url = serializers.SerializerMethodField()
    file_size_human = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = [
            'id', 'file', 'file_url', 'title', 'description',
            'media_type', 'uploaded_by', 'file_size', 'file_size_human',
            'content_type', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['file_size', 'content_type', 'created_at', 'updated_at']
        swagger_schema = {
            'required': ['file'],
            'properties': {
                'file': {
                    'type': openapi.TYPE_FILE,
                    'description': 'The media file to upload'
                },
                'title': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Title for the media file'
                },
                'description': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Description for the media file'
                },
                'media_type': {
                    'type': openapi.TYPE_STRING,
                    'enum': ['image', 'video', 'audio', 'document', 'other'],
                    'description': 'Type of media'
                },
                'uploaded_by': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Username of the uploader'
                },
                'is_active': {
                    'type': openapi.TYPE_BOOLEAN,
                    'description': 'Whether the media is active'
                }
            }
        }
    
    def get_file_url(self, obj):
        """Get the full URL of the file"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size_human(self, obj):
        """Convert file size to human readable format"""
        if obj.file_size:
            file_size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if file_size < 1024.0:
                    return f"{file_size:.2f} {unit}"
                file_size /= 1024.0
            return f"{file_size:.2f} TB"
        return None
    
    def create(self, validated_data):
        """Create a new media instance"""
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing media instance"""
        return super().update(instance, validated_data)


class MediaUploadSerializer(serializers.Serializer):
    """Serializer for media upload with file field"""
    
    file = serializers.FileField(required=True)
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    media_type = serializers.ChoiceField(
        choices=Media.MEDIA_TYPE_CHOICES,
        required=False,
        default='image'
    )
    uploaded_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    class Meta:
        swagger_schema = {
            'required': ['file'],
            'properties': {
                'file': {
                    'type': openapi.TYPE_FILE,
                    'description': 'The media file to upload',
                    'format': 'binary'
                },
                'title': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Title for the media file (optional)'
                },
                'description': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Description for the media file (optional)'
                },
                'media_type': {
                    'type': openapi.TYPE_STRING,
                    'enum': ['image', 'video', 'audio', 'document', 'other'],
                    'description': 'Type of media (defaults to image)'
                },
                'uploaded_by': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Username of the uploader (optional)'
                }
            }
        }
    
    def validate_file(self, value):
        """Validate the uploaded file"""
        # Get file size
        file_size = value.size
        max_size_mb = 50  # 50MB limit
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
        
        # Validate content type based on media type
        content_type = value.content_type
        allowed_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        allowed_video_types = ['video/mp4', 'video/webm', 'video/quicktime']
        allowed_audio_types = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp3']
        allowed_document_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain'
        ]
        
        # Basic content type validation
        return value
