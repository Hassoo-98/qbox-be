from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomHomeOwner
from .serializers import (
    HomeOwnerSerializer,
    HomeOwnerCreateSerializer,
    HomeOwnerStatusUpdateSerializer,
)
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

# Swagger Helper for Home Owner
swagger = SwaggerHelper(tag="Home Owner")


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


class HomeOwnerListAPIView(generics.ListAPIView):
    '''
    Get: list all home owners with pagination and filters
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone_number"]
    ordering_fields = ["name", "email", "phone_number"]
    ordering = ["-date_joined"]

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all home owners",
            description="Retrieve a paginated list of all home owners with optional filtering by search query, ordering, and active status.",
            serializer=HomeOwnerSerializer
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
            "message": "List Home Owners"
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


class HomeOwnerCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new home owner
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new home owner",
            description="Register a new home owner with personal information and property details.",
            serializer=HomeOwnerCreateSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                home_owner = serializer.save()
                home_owner_data = HomeOwnerSerializer(home_owner).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": home_owner_data,
                    "message": "Home Owner created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class HomeOwnerDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single home owner
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get home owner details",
            description="Retrieve detailed information about a specific home owner including personal info and current status.",
            serializer=HomeOwnerSerializer
        )
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Home Owner"
        }, status=status.HTTP_200_OK)


class HomeOwnerUpdateAPIView(generics.UpdateAPIView):
    '''
    Put: Update a home owner
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update home owner",
            description="Update home owner information such as name, phone, or active status.",
            serializer=HomeOwnerSerializer
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
            "message": "Home Owner updated successfully"
        }, status=status.HTTP_200_OK)


class HomeOwnerStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update home owner active status
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Home Owner] Update home owner status",
        operation_description="Update home owner active status. Activating a home owner enables their account access. Deactivating temporarily suspends their access.",
        tags=["Home Owner"],
        request_body=HomeOwnerStatusUpdateSerializer,
        responses={
            200: create_success_response(
                get_serializer_schema(HomeOwnerSerializer),
                description="Home owner status updated successfully"
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
            "data": HomeOwnerSerializer(serializer.instance).data,
            "message": "Home Owner status updated successfully"
        }, status=status.HTTP_200_OK)


class HomeOwnerDeleteAPIView(generics.DestroyAPIView):
    '''
    Delete: Remove a home owner
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete home owner",
            description="Remove a home owner from the system. This action is permanent and cannot be undone."
        )
    )
    def destroy(self, request, *args, **kwargs):
        home_owner = self.get_object()
        home_owner_data = HomeOwnerSerializer(home_owner).data
        home_owner.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": home_owner_data,
            "message": "Home Owner deleted successfully"
        }, status=status.HTTP_200_OK)
