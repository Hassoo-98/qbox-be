from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomStaff
from .serializers import (
    StaffSerializer,
    StaffCreateSerializer,
    StaffStatusUpdateSerializer,
)
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

# Swagger Helper for Staff
swagger = SwaggerHelper(tag="Staff")


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


class StaffListAPIView(generics.ListAPIView):
    '''
    Get: list all staff with pagination and filters
    '''
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone_number"]
    ordering_fields = ["name", "email", "phone_number"]
    ordering = ["-date_joined"]

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all staff",
            description="Retrieve a paginated list of all staff members with optional filtering by search query, ordering, active status, and role.",
            serializer=StaffSerializer
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
            "message": "List Staff"
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
                "page": 1,
                "limit": queryset.count() if queryset.count() < self.pagination_class.page_size else self.pagination_class.page_size,
                "hasMore": False
            }
        })


class StaffCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new staff member
    '''
    queryset = CustomStaff.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new staff member",
            description="Register a new staff member with personal information and role assignment.",
            serializer=StaffCreateSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                staff = serializer.save()
                staff_data = StaffSerializer(staff).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": staff_data,
                    "message": "Staff created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class StaffDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single staff member
    '''
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get staff details",
            description="Retrieve detailed information about a specific staff member including personal info, role, and current status.",
            serializer=StaffSerializer
        )
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Staff"
        }, status=status.HTTP_200_OK)


class StaffUpdateAPIView(generics.UpdateAPIView):
    '''
    Put: Update a staff member
    '''
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update staff",
            description="Update staff information such as name, phone, role, or active status.",
            serializer=StaffSerializer
        )
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Staff updated successfully"
        }, status=status.HTTP_200_OK)


class StaffStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update staff active status
    '''
    queryset = CustomStaff.objects.all()
    serializer_class = StaffStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Staff] Update staff status",
        operation_description="Update staff active status. Activating a staff member enables their account access. Deactivating temporarily suspends their access.",
        tags=["Staff"],
        request_body=StaffStatusUpdateSerializer,
        responses={
            200: create_success_response(
                get_serializer_schema(StaffSerializer),
                description="Staff status updated successfully"
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": StaffSerializer(serializer.instance).data,
            "message": "Staff status updated successfully"
        }, status=status.HTTP_200_OK)


class StaffDeleteAPIView(generics.DestroyAPIView):
    '''
    Delete: Remove a staff member
    '''
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete staff",
            description="Remove a staff member from the system. This action is permanent and cannot be undone."
        )
    )
    def destroy(self, request, *args, **kwargs):
        staff = self.get_object()
        staff_data = StaffSerializer(staff).data
        staff.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": staff_data,
            "message": "Staff deleted successfully"
        }, status=status.HTTP_200_OK)
