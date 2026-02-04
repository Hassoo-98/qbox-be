from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Qbox
from .serializers import QboxSerializer, QboxListSerializer, QboxCreateSerializer, QboxUpdateSerializer
from utils.swagger_schema import (
    ValidationErrorResponse,
    NotFoundResponse,
)

# Swagger Tag
QBOX_TAG = 'QBox'


class QboxListAPIView(generics.ListAPIView):
    """
    GET: List all qboxes
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="[QBox] List all QBoxes",
        operation_description="Retrieve a paginated list of all QBoxes.",
        tags=[QBOX_TAG],
        responses={
            200: openapi.Response(
                description="QBoxes retrieved successfully",
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
            "message": "Qbox List"
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
            "message": "Qbox List"
        })


class QboxDetailAPIView(generics.RetrieveAPIView):
    """
    GET: Get qbox details by ID
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        operation_summary="[QBox] Get QBox details",
        operation_description="Retrieve detailed information about a specific QBox by ID.",
        tags=[QBOX_TAG],
        responses={
            200: openapi.Response(
                description="QBox details retrieved successfully",
                schema=QboxSerializer
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
            "message": "Qbox Details"
        })


class QboxByIdAPIView(generics.RetrieveAPIView):
    """
    GET: Get qbox details by qbox_id
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "qbox_id"

    @swagger_auto_schema(
        operation_summary="[QBox] Get QBox by QBox ID",
        operation_description="Retrieve QBox details using the unique QBox ID.",
        tags=[QBOX_TAG],
        responses={
            200: openapi.Response(
                description="QBox retrieved successfully",
                schema=QboxSerializer
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
            "message": "Qbox Details"
        })


class QboxCreateAPIView(generics.CreateAPIView):
    """
    POST: Create a new qbox
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="[QBox] Create QBox",
        operation_description="Create a new QBox with location and owner details.",
        tags=[QBOX_TAG],
        request_body=QboxCreateSerializer,
        responses={
            201: openapi.Response(
                description="QBox created successfully",
                schema=QboxSerializer
            ),
            400: ValidationErrorResponse,
            401: openapi.Response(description="Authentication required"),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qbox = serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "data": QboxSerializer(qbox).data,
            "message": "Qbox created successfully"
        }, status=status.HTTP_201_CREATED)


class QboxUpdateAPIView(generics.UpdateAPIView):
    """
    PUT/PATCH: Update qbox
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[QBox] Update QBox",
        operation_description="Update QBox information such as location or owner details.",
        tags=[QBOX_TAG],
        request_body=QboxUpdateSerializer,
        responses={
            200: openapi.Response(
                description="QBox updated successfully",
                schema=QboxSerializer
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
        qbox = serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": QboxSerializer(qbox).data,
            "message": "Qbox updated successfully"
        })


class QboxDeleteAPIView(generics.DestroyAPIView):
    """
    DELETE: Delete qbox
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        operation_summary="[QBox] Delete QBox",
        operation_description="Remove a QBox from the system.",
        tags=[QBOX_TAG],
        responses={
            200: openapi.Response(
                description="QBox deleted successfully",
                schema=QboxSerializer
            ),
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = QboxSerializer(instance).data
        instance.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": data,
            "message": "Qbox deleted successfully"
        })
