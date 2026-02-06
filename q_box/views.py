from rest_framework import generics, status,permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Qbox, QboxAccessQRCode, QboxAccessUser
from .serializers import (
    QboxSerializer,
    QboxCreateSerializer,
    QboxStatusUpdateSerializer,
    VerifyQboxIdSerializer,
    QboxAccessQRCodeSerializer,
    QboxAccessQRCodeCreateSerializer,
    QboxAccessQRCodeListSerializer,
    QboxAccessQRCodeUpdateSerializer,
    QboxAccessQRCodeHistorySerializer,
    QboxAccessQRCodeStatusUpdateSerializer,
    QboxAccessUserSerializer,
    QboxAccessRequestSerializer,
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


# QR Code APIs

class QboxAccessQRCodeListAPIView(generics.ListAPIView):
    """
    Get: List all access QR codes for a Qbox
    """
    queryset = QboxAccessQRCode.objects.all()
    serializer_class = QboxAccessQRCodeListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "location"]
    ordering_fields = ["created_at", "expires_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        qbox_id = self.request.query_params.get('qbox_id')
        is_active = self.request.query_params.get('is_active')
        
        if qbox_id:
            queryset = queryset.filter(qbox__qbox_id=qbox_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="List access QR codes",
        operation_description="Retrieve a list of access QR codes for QBoxes with optional filtering."
    )
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
            "data": serializer.data,
            "message": "List QR codes"
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
            "message": "List QR codes"
        })


class QboxAccessQRCodeCreateAPIView(generics.CreateAPIView):
    """
    Post: Create a new access QR code for a Qbox
    """
    serializer_class = QboxAccessQRCodeCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Get the homeowner from the request
        context['homeowner'] = self.request.user
        return context

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="Create access QR code",
        operation_description="Create a new access QR code for a Qbox. If duration_type is 'days', valid_duration is in days. If 'minutes', it's in minutes."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        qr_code = serializer.save()
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "data": QboxAccessQRCodeSerializer(qr_code).data,
            "message": "QR code created successfully"
        }, status=status.HTTP_201_CREATED)


class QboxAccessQRCodeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get: Get QR code details
    Patch: Update QR code
    Delete: Delete QR code
    """
    queryset = QboxAccessQRCode.objects.all()
    serializer_class = QboxAccessQRCodeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QboxAccessQRCodeUpdateSerializer
        return QboxAccessQRCodeSerializer

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="Get QR code details",
        operation_description="Retrieve details of an access QR code."
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "QR code details"
        })

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="Update QR code",
        operation_description="Update an access QR code's details."
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
            "data": QboxAccessQRCodeSerializer(instance).data,
            "message": "QR code updated successfully"
        })

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="Delete QR code",
        operation_description="Delete an access QR code."
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": None,
            "message": "QR code deleted successfully"
        })


class QboxAccessQRCodeAccessAPIView(generics.CreateAPIView):
    """
    Post: Access Qbox via QR code
    """
    serializer_class = QboxAccessRequestSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="Access Qbox via QR code",
        operation_description="Validate and use an access QR code to gain entry to a Qbox."
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data['access_token']
        user_identifier = serializer.validated_data['user_identifier']
        user_name = serializer.validated_data.get('user_name', '')
        
        try:
            qr_code = QboxAccessQRCode.objects.get(access_token=access_token)
        except QboxAccessQRCode.DoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "data": None,
                "message": "Invalid QR code"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if QR code is valid
        if not qr_code.is_valid():
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "This QR code has expired or reached maximum users"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already has access
        existing_access = QboxAccessUser.objects.filter(
            qr_code=qr_code,
            user_identifier=user_identifier
        ).exists()
        
        if existing_access:
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "message": "User already has access",
                    "qbox": {
                        "id": str(qr_code.qbox.id),
                        "qbox_id": qr_code.qbox.qbox_id,
                        "location": qr_code.location,
                        "address": qr_code.address
                    }
                },
                "message": "Access already granted"
            }, status=status.HTTP_200_OK)
        
        # Increment usage and record access
        if qr_code.increment_usage():
            access_user = QboxAccessUser.objects.create(
                qr_code=qr_code,
                user_identifier=user_identifier,
                user_name=user_name,
                access_type="qr_code"
            )
            
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "message": "Access granted successfully",
                    "qbox": {
                        "id": str(qr_code.qbox.id),
                        "qbox_id": qr_code.qbox.qbox_id,
                        "location": qr_code.location,
                        "address": qr_code.address
                    },
                    "access": {
                        "expires_at": qr_code.expires_at,
                        "remaining_users": qr_code.max_users - qr_code.current_users
                    }
                },
                "message": "Access granted successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "Maximum users reached for this QR code"
            }, status=status.HTTP_400_BAD_REQUEST)


class QboxAccessUsersListAPIView(generics.ListAPIView):
    """
    Get: List users who have accessed via a QR code
    """
    serializer_class = QboxAccessUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        qr_code_id = self.kwargs.get('id')
        return QboxAccessUser.objects.filter(qr_code_id=qr_code_id)

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="List QR code access users",
        operation_description="List all users who have accessed via a specific QR code."
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "List access users"
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
            "message": "List access users"
        })


# ==================== QR Code History Log API ====================

class QboxAccessQRCodeHistoryAPIView(generics.ListAPIView):
    """
    Get: List all QR codes with their status history
    Returns: qr_name, status (Active/Expired), validforUsers, expiresIn
    """
    queryset = QboxAccessQRCode.objects.all()
    serializer_class = QboxAccessQRCodeHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["qbox__qbox_id", "name", "qbox__homeowner_name_snapshot"]
    ordering_fields = ["created_at", "expires_at"]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        tags=["QBox QR Code History"],
        operation_summary="QR Code History Log",
        operation_description="Get a list of all QR codes with their status, valid users remaining, and expiration time."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class QboxAccessQRCodeStatusUpdateAPIView(generics.UpdateAPIView):
    """
    Patch: Update QR code status (Active/Inactive)
    """
    queryset = QboxAccessQRCode.objects.all()
    serializer_class = QboxAccessQRCodeStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        tags=["QBox QR Code"],
        operation_summary="Update QR code status",
        operation_description="Change the active status of a QR code (Active or Inactive)."
    )
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data.get('status')
        is_active = new_status == "Active"
        instance.is_active = is_active
        instance.save(update_fields=['is_active', 'updated_at'])
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": QboxAccessQRCodeSerializer(instance).data,
            "message": f"QR code status updated to {new_status}"
        })
