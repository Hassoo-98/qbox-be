import os
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Media
from .serializers import MediaSerializer, MediaUploadSerializer


class MediaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing media files (CRUD operations)
    
    Provides endpoints for:
    - List all media files
    - Retrieve a single media file
    - Create/upload new media file
    - Update media file
    - Delete media file
    - Custom actions: upload, bulk_delete
    """
    
    queryset = Media.objects.filter(is_active=True)
    serializer_class = MediaSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = Media.objects.filter(is_active=True)
        
        # Filter by media type
        media_type = self.request.query_params.get('media_type')
        if media_type:
            queryset = queryset.filter(media_type=media_type)
        
        # Filter by uploaded by
        uploaded_by = self.request.query_params.get('uploaded_by')
        if uploaded_by:
            queryset = queryset.filter(uploaded_by=uploaded_by)
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="List all media files with optional filtering.",
        manual_parameters=[
            openapi.Parameter(
                'media_type',
                openapi.IN_QUERY,
                description="Filter by media type (image, video, audio, document, other)",
                type=openapi.TYPE_STRING,
                enum=['image', 'video', 'audio', 'document', 'other']
            ),
            openapi.Parameter(
                'uploaded_by',
                openapi.IN_QUERY,
                description="Filter by uploader username",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in title or description",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            ),
        ],
        responses={
            200: MediaSerializer(many=True),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def list(self, request, *args, **kwargs):
        """List all media files"""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a single media file by ID.",
        responses={
            200: MediaSerializer,
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single media file"""
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new media file with file upload.",
        request_body=MediaUploadSerializer,
        responses={
            201: MediaSerializer,
            400: "Bad Request - Validation errors",
            500: "Internal Server Error"
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new media file"""
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a media file by ID.",
        request_body=MediaSerializer,
        responses={
            200: MediaSerializer,
            400: "Bad Request - Validation errors",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a media file"""
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update a media file by ID.",
        request_body=MediaSerializer,
        responses={
            200: MediaSerializer,
            400: "Bad Request - Validation errors",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a media file"""
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a media file by ID (soft delete).",
        responses={
            204: "No Content",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a media file (soft delete)"""
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_description="Upload a single file with optional metadata.",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="File to upload",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'title',
                openapi.IN_FORM,
                description="Title for the media file",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                description="Description for the media file",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'media_type',
                openapi.IN_FORM,
                description="Media type (image, video, audio, document, other)",
                type=openapi.TYPE_STRING,
                enum=['image', 'video', 'audio', 'document', 'other']
            ),
            openapi.Parameter(
                'uploaded_by',
                openapi.IN_FORM,
                description="Username of the uploader",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            201: MediaSerializer,
            400: "Bad Request - Validation errors",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        Custom action for uploading a single file
        POST /api/media/upload/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            media = serializer.save()
            response_serializer = MediaSerializer(media, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Get download URL for a media file.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'download_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'filename': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """
        Get download URL for a media file
        GET /api/media/{id}/download/
        """
        media = self.get_object()
        return Response({
            'download_url': request.build_absolute_uri(media.file.url),
            'filename': os.path.basename(media.file.name)
        })
    
    @swagger_auto_schema(
        operation_description="Restore a soft-deleted media file.",
        responses={
            200: MediaSerializer,
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted media file
        POST /api/media/{id}/restore/
        """
        try:
            media = Media.objects.get(pk=pk, is_active=False)
            media.is_active = True
            media.save()
            serializer = MediaSerializer(media, context={'request': request})
            return Response(serializer.data)
        except Media.DoesNotExist:
            return Response(
                {'error': 'Media not found or already active'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Delete multiple media files by IDs.",
        manual_parameters=[
            openapi.Parameter(
                'ids',
                openapi.IN_QUERY,
                description="Comma-separated list of media IDs to delete",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'deleted': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Delete multiple media files by IDs
        DELETE /api/media/bulk-delete/?ids=1,2,3
        """
        ids = request.query_params.get('ids')
        if not ids:
            return Response(
                {'error': 'IDs parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        id_list = [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]
        deleted_count = Media.objects.filter(id__in=id_list).delete()[0]
        
        return Response({
            'deleted': deleted_count,
            'message': f'Successfully deleted {deleted_count} media file(s)'
        })
