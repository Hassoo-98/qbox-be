from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import City, Area
from .serializers import (
    CitySerializer,
    CityCreateSerializer,
    CityStatusUpdateSerializer,
    AreaSerializer,
    AreaCreateSerializer,
    AreaStatusUpdateSerializer,
)
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

# Swagger Helper for Location
swagger = SwaggerHelper(tag="Location")


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


# ==================== City Views ====================

class CityListAPIView(generics.ListAPIView):
    '''
    Get: list all cities with pagination and filters
    '''
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "name_ar", "code"]
    ordering_fields = ["name", "name_ar", "code"]
    ordering = ["name"]

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all cities",
            description="Retrieve a paginated list of all cities with optional filtering by search query, ordering, active status, state, and country.",
            serializer=CitySerializer
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
            "message": "List Cities"
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


class CityCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new city
    '''
    queryset = City.objects.all()
    serializer_class = CityCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new city",
            description="Register a new city with name, state, and country information.",
            serializer=CityCreateSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                city = serializer.save()
                city_data = CitySerializer(city).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": city_data,
                    "message": "City created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CityDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single city
    '''
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get city details",
            description="Retrieve detailed information about a specific city including name, state, country, and associated areas.",
            serializer=CitySerializer
        )
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get City"
        }, status=status.HTTP_200_OK)


class CityUpdateAPIView(generics.UpdateAPIView):
    '''
    Put: Update a city
    '''
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update city",
            description="Update city information such as name, state, country, or active status.",
            serializer=CitySerializer
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
            "message": "City updated successfully"
        }, status=status.HTTP_200_OK)


class CityStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update city active status
    '''
    queryset = City.objects.all()
    serializer_class = CityStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Location] Update city status",
        operation_description="Update city active status. Deactivating a city will also deactivate all associated areas.",
        tags=["Location"],
        request_body=CityStatusUpdateSerializer,
        responses={
            200: create_success_response(
                get_serializer_schema(CitySerializer),
                description="City status updated successfully"
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
            "data": CitySerializer(serializer.instance).data,
            "message": "City status updated successfully"
        }, status=status.HTTP_200_OK)


class CityDeleteAPIView(generics.DestroyAPIView):
    '''
    Delete: Remove a city
    '''
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete city",
            description="Remove a city from the system. This action will also remove all associated areas and cannot be undone."
        )
    )
    def destroy(self, request, *args, **kwargs):
        city = self.get_object()
        city_data = CitySerializer(city).data
        city.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": city_data,
            "message": "City deleted successfully"
        }, status=status.HTTP_200_OK)


# ==================== Area Views ====================

class AreaListAPIView(generics.ListAPIView):
    '''
    Get: list all areas with pagination and filters
    '''
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "city__name"]
    ordering_fields = ["name", "city__name"]
    ordering = ["name"]

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all areas",
            description="Retrieve a paginated list of all areas with optional filtering by search query, ordering, active status, and city.",
            serializer=AreaSerializer
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
            "message": "List Areas"
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


class AreaCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new area
    '''
    queryset = Area.objects.all()
    serializer_class = AreaCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new area",
            description="Register a new area with name and city assignment.",
            serializer=AreaCreateSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                area = serializer.save()
                area_data = AreaSerializer(area).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": area_data,
                    "message": "Area created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AreaDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single area
    '''
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get area details",
            description="Retrieve detailed information about a specific area including name, city, and active status.",
            serializer=AreaSerializer
        )
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Area"
        }, status=status.HTTP_200_OK)


class AreaUpdateAPIView(generics.UpdateAPIView):
    '''
    Put: Update an area
    '''
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update area",
            description="Update area information such as name, city assignment, or active status.",
            serializer=AreaSerializer
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
            "message": "Area updated successfully"
        }, status=status.HTTP_200_OK)


class AreaStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update area active status
    '''
    queryset = Area.objects.all()
    serializer_class = AreaStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Location] Update area status",
        operation_description="Update area active status. This controls whether deliveries can be made to this area.",
        tags=["Location"],
        request_body=AreaStatusUpdateSerializer,
        responses={
            200: create_success_response(
                get_serializer_schema(AreaSerializer),
                description="Area status updated successfully"
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
            "data": AreaSerializer(serializer.instance).data,
            "message": "Area status updated successfully"
        }, status=status.HTTP_200_OK)


class AreaDeleteAPIView(generics.DestroyAPIView):
    '''
    Delete: Remove an area
    '''
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete area",
            description="Remove an area from the system. This action is permanent and cannot be undone."
        )
    )
    def destroy(self, request, *args, **kwargs):
        area = self.get_object()
        area_data = AreaSerializer(area).data
        area.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": area_data,
            "message": "Area deleted successfully"
        }, status=status.HTTP_200_OK)
