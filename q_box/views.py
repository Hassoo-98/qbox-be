from rest_framework import generics, status,permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Qbox
from .serializers import (
    QboxSerializer,
    QboxCreateSerializer,
    QboxStatusUpdateSerializer,
    VerifyQboxIdSerializer,
)
from home_owner.models import CustomHomeOwner
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)
swagger = SwaggerHelper(tag="QBox")
class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


class QboxListAPIView(generics.ListAPIView):
    '''
    Get: list all QBoxes with pagination and filters
    '''
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["qbox_id", "homeowner_name_snapshot", "city_snapshot"]
    ordering_fields = ["qbox_id", "created_at"]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all QBoxes",
            description="Retrieve a paginated list of all QBoxes with optional filtering by search query, ordering, active status, and current status.",
            serializer=QboxSerializer,
             tags=["QBox"]
        )
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
            "message": "List QBoxes"
        })

    def get(self, request, *args, **kwargs):
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
                "page": 1,
                "limit": queryset.count() if queryset.count() < self.pagination_class.page_size else self.pagination_class.page_size,
                "hasMore": False
            }
        })


class QboxCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new QBox
    '''
    queryset = Qbox.objects.all()
    serializer_class = QboxCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new QBox",
            description="Register a new QBox with location details and home owner assignment.",
            serializer=QboxCreateSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                qbox = serializer.save()
                qbox_data = QboxSerializer(qbox).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": qbox_data,
                    "message": "QBox created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class QboxDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single QBox
    '''
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get QBox details",
            description="Retrieve detailed information about a specific QBox including location, home owner, and current status.",
            serializer=QboxSerializer
        )
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get QBox"
        }, status=status.HTTP_200_OK)


class QboxUpdateAPIView(generics.UpdateAPIView):
    '''
    Put: Update a QBox
    '''
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update QBox",
            description="Update QBox information such as location, home owner assignment, or active status.",
            serializer=QboxSerializer
        )
    )
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "QBox updated successfully"
        }, status=status.HTTP_200_OK)
class QboxStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update QBox status
    '''
    queryset = Qbox.objects.all()
    serializer_class = QboxStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[QBox] Update QBox status",
        operation_description="Update QBox status and active state. This controls whether the QBox can receive deliveries.",
        tags=["QBox"],
        responses={
            200: create_success_response(
                get_serializer_schema(QboxSerializer),
                description="QBox status updated successfully"
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": QboxSerializer(serializer.instance).data,
            "message": "QBox status updated successfully"
        }, status=status.HTTP_200_OK)


class QboxDeleteAPIView(generics.DestroyAPIView):
    '''
    Delete: Remove a QBox
    '''
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete QBox",
            description="Remove a QBox from the system. This action is permanent and cannot be undone."
        )
    )
    def delete(self, request, *args, **kwargs):
        qbox = self.get_object()
        qbox_data = QboxSerializer(qbox).data
        qbox.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": qbox_data,
            "message": "QBox deleted successfully"
        }, status=status.HTTP_200_OK)


class VerifyQboxIdAPIView(generics.CreateAPIView):
    """
    Post: Verify QBox ID
    """
    serializer_class = VerifyQboxIdSerializer
    permission_classes = [permissions.AllowAny]
    
    
    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Verify QBox ID",
            description="Verify a QBox device ID. The QBox must exist in the system. No user assignment required.",
            serializer=VerifyQboxIdSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        qbox_id = serializer.validated_data['qbox_id']
        
        try:
            qbox = Qbox.objects.get(qbox_id=qbox_id)
        except Qbox.DoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "data": None,
                "message": "QBox with this ID not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data":None,
            "message": "QBox verified successfully"
        }, status=status.HTTP_200_OK)
