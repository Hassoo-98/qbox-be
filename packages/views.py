from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Package
from .serializers import (
    PackageSerializer, PackageListSerializer,
    PackageCreateSerializer, PackageUpdateSerializer
)
from utils.swagger_schema import (
    ValidationErrorResponse,
    NotFoundResponse,
)

# Swagger Tag
PACKAGES_TAG = 'Packages'


class PackageListAPIView(generics.ListAPIView):
    """
    GET: List all packages
    """
    queryset = Package.objects.all()
    serializer_class = PackageListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="[Packages] List all packages",
        operation_description="Retrieve a paginated list of all packages.",
        tags=[PACKAGES_TAG],
        responses={
            200: openapi.Response(
                description="Packages retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            401: openapi.Response(description="Authentication required"),
        }
    )
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

    @swagger_auto_schema(
        operation_summary="[Packages] Get package details",
        operation_description="Retrieve detailed information about a specific package by ID.",
        tags=[PACKAGES_TAG],
        responses={
            200: openapi.Response(
                description="Package details retrieved successfully",
                schema=PackageSerializer
            ),
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
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

    @swagger_auto_schema(
        operation_summary="[Packages] Get package by tracking ID",
        operation_description="Retrieve package details using tracking ID.",
        tags=[PACKAGES_TAG],
        responses={
            200: openapi.Response(
                description="Package retrieved successfully",
                schema=PackageSerializer
            ),
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
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
    """
    queryset = Package.objects.all()
    serializer_class = PackageListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="[Packages] List packages by QBox ID",
        operation_description="Retrieve all packages associated with a specific QBox ID.",
        tags=[PACKAGES_TAG],
        responses={
            200: openapi.Response(
                description="Packages retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="No packages found"),
        }
    )
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

    @swagger_auto_schema(
        operation_summary="[Packages] Create package",
        operation_description="Create a new package with delivery details.",
        tags=[PACKAGES_TAG],
        request_body=PackageCreateSerializer,
        responses={
            201: openapi.Response(
                description="Package created successfully",
                schema=PackageSerializer
            ),
            400: ValidationErrorResponse,
            401: openapi.Response(description="Authentication required"),
        }
    )
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

    @swagger_auto_schema(
        operation_summary="[Packages] Update package",
        operation_description="Update package information such as status, weight, or delivery details.",
        tags=[PACKAGES_TAG],
        request_body=PackageUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Package updated successfully",
                schema=PackageSerializer
            ),
            400: ValidationErrorResponse,
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
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

    @swagger_auto_schema(
        operation_summary="[Packages] Delete package",
        operation_description="Remove a package from the system.",
        tags=[PACKAGES_TAG],
        responses={
            200: openapi.Response(
                description="Package deleted successfully",
                schema=PackageSerializer
            ),
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
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
