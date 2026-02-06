from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from core.authentication import CookieJWTAuthentication
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
    create_paginated_response,   
)

swagger = SwaggerHelper(tag="Staff")


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


def get_wrapped_response_schema(inner_schema, description="Success response"):
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True),
            "statusCode": openapi.Schema(type=openapi.TYPE_INTEGER, example=200),
            "message": openapi.Schema(type=openapi.TYPE_STRING),
            "data": inner_schema,
        },
        description=description,
    )


class StaffListAPIView(generics.ListAPIView):
    """
    GET: List all staff with pagination, search and ordering
    """
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone_number"]
    ordering_fields = ["name", "email", "phone_number"]
    ordering = ["-date_joined"]

    @swagger_auto_schema(
        tags=["Staff"],
        operation_summary="[Staff] List all staff (paginated)",
        operation_description=(
            "Retrieve a paginated list of staff members.\n\n"
            "Supports:\n"
            "- Search: name, email, phone_number\n"
            "- Ordering: name, email, phone_number (prefix with - for descending)\n"
            "- Pagination: ?page= &limit="
        ),
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number", default=1),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Items per page (max 100)", default=10),
            openapi.Parameter("search", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Search term"),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Ordering field(s), e.g. name,-email"),
        ],
        responses={
            200: create_paginated_response(  
                get_serializer_schema(StaffSerializer, many=True),
                tag="Staff items"
            ),
            401: "Unauthorized",
            **COMMON_RESPONSES,
        }
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
            "data": {
                "items": serializer.data,
                "total": len(serializer.data),
                "page": 1,
                "limit": queryset.count() if queryset.count() < self.pagination_class.page_size else self.pagination_class.page_size,
                "hasMore": False
            },
            "message": "List Staff"
        })

    def get_paginated_response(self, data):
        # No decorator needed here anymore
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


class StaffCreateAPIView(generics.CreateAPIView):
    queryset = CustomStaff.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Staff"],
        operation_summary="[Staff] Create a new staff member",
        operation_description="Register a new staff member with personal information and role assignment.",
        responses={
            201: get_wrapped_response_schema(
                get_serializer_schema(StaffSerializer),
                "Staff created successfully"
            ),
            400: ValidationErrorResponse,
            401: "Unauthorized",
            **COMMON_RESPONSES,
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        staff_data = StaffSerializer(staff).data
        return Response({
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "data": staff_data,
            "message": "Staff created successfully"
        }, status=status.HTTP_201_CREATED)




class StaffDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        tags=["Staff"],
        operation_summary="[Staff] Get staff details",
        operation_description="Retrieve detailed information about a specific staff member.",
        responses={
            200: get_wrapped_response_schema(
                get_serializer_schema(StaffSerializer),
                "Staff details retrieved"
            ),
            404: NotFoundResponse,
            401: "Unauthorized",
        }
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Staff"
        })


class StaffUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        tags=["Staff"],
        operation_summary="[Staff] Update staff information",
        operation_description="Update name, phone, role, active status, etc. Use PATCH for partial updates.",
        responses={
            200: get_wrapped_response_schema(
                get_serializer_schema(StaffSerializer),
                "Staff updated successfully"
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
            401: "Unauthorized",
        }
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
            "message": "Staff updated successfully"
        })


class StaffStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomStaff.objects.all()
    serializer_class = StaffStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        tags=["Staff"],
        operation_summary="[Staff] Update staff active status",
        operation_description="Activate or deactivate a staff member (is_active field).",
        responses={
            200: get_wrapped_response_schema(
                get_serializer_schema(StaffSerializer),
                "Staff status updated successfully"
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
            401: "Unauthorized",
        }
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": StaffSerializer(serializer.instance).data,
            "message": "Staff status updated successfully"
        })


class StaffDeleteAPIView(generics.DestroyAPIView):
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        tags=["Staff"],
        operation_summary="[Staff] Delete a staff member",
        operation_description="Permanently remove a staff member. Returns data of the deleted record.",
        responses={
            200: get_wrapped_response_schema(
                get_serializer_schema(StaffSerializer),
                "Staff deleted successfully"
            ),
            404: NotFoundResponse,
            401: "Unauthorized",
        }
    )
    def delete(self, request, *args, **kwargs):
        staff = self.get_object()
        staff_data = StaffSerializer(staff).data
        staff.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": staff_data,
            "message": "Staff deleted successfully"
        })