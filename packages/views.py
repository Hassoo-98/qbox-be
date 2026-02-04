from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Package
from .serializers import (
    PackageSerializer, PackageListSerializer,
    PackageCreateSerializer, PackageUpdateSerializer
)

class PackageListAPIView(generics.ListAPIView):
    """
    GET: List all packages
    """
    queryset = Package.objects.all()
    serializer_class = PackageListSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                "items": data,
                "total": self.paginator.page.paginator.count,
                "page": self.paginator.page.number,
                "limit": self.paginator.page_size,
                "hasMore": self.paginator.page.has_next(),
            },
            "message": "Package List"
        })

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                "items": serializer.data,
                "total": len(serializer.data),
                "hasMore": False
            },
            "message": "Package List"
        })

class PackageDetailAPIView(generics.RetrieveAPIView):
    """
    GET: Get package details by ID
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Package Details"
        })

class PackageByTrackingIdAPIView(generics.RetrieveAPIView):
    """
    GET: Get package by tracking_id
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "tracking_id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Package Details"
        })

class PackagesByQboxIdAPIView(generics.ListAPIView):
    """
    GET: List all packages for a specific qbox by qbox UUID
    URL: /api/packages/by-qbox/<qbox_uuid>/
    Example: /api/packages/by-qbox/be3137b3-976a-4e86-9d44-a926220e52bb/
    """
    queryset = Package.objects.all()
    serializer_class = PackageListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qbox_uuid = self.kwargs.get('qbox_uuid')
        if qbox_uuid:
            return Package.objects.filter(qbox__id=qbox_uuid)
        return Package.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "data": [],
                "message": "No packages found for this qbox"
            }, status=status.HTTP_404_NOT_FOUND)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                "items": serializer.data,
                "total": len(serializer.data),
                "hasMore": False
            },
            "message": "Package List"
        })

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                "items": data,
                "total": self.paginator.page.paginator.count,
                "page": self.paginator.page.number,
                "limit": self.paginator.page_size,
                "hasMore": self.paginator.page.has_next(),
            },
            "message": "Package List"
        })

class PackageCreateAPIView(generics.CreateAPIView):
    """
    POST: Create a new package
    """
    queryset = Package.objects.all()
    serializer_class = PackageCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        package = serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "data": PackageSerializer(package).data,
            "message": "Package created successfully"
        }, status=status.HTTP_201_CREATED)

class PackageUpdateAPIView(generics.UpdateAPIView):
    """
    PUT/PATCH: Update package
    """
    queryset = Package.objects.all()
    serializer_class = PackageUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        package = serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": PackageSerializer(package).data,
            "message": "Package updated successfully"
        })

class PackageDeleteAPIView(generics.DestroyAPIView):
    """
    DELETE: Delete package
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = PackageSerializer(instance).data
        instance.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": data,
            "message": "Package deleted successfully"
        })
