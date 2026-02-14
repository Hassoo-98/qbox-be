from rest_framework import generics, status, permissions
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
    HomeOwnerLoginSerializer,
    HomeOwnerResetPasswordSerializer,
)
from q_box.serializers import VerifyQboxIdSerializer
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

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
    permission_classes = []
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

class HomeOwnerCreateAPIView(generics.CreateAPIView):
    """
    POST: Register new home owner + link QBox + optional base64 image
    """
    queryset = CustomHomeOwner.objects.none()
    serializer_class = HomeOwnerCreateSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Register New Home Owner",
        operation_description=(
            "Creates a new home owner account, links it to a QBox device, "
            "and optionally attaches an installation photo.\n\n"
            "**Image upload options (in JSON payload):**\n"
            "- `installation_image_base64`: base64 data URI (data:image/jpeg;base64,...)\n"
            "  → Recommended only for small images (< 2–3 MB)\n"
            "- For large images or better performance: upload separately to `/api/media/upload/` "
            "and send the returned URL in `installation.qbox_image_url` (future field)\n\n"
            "All fields are sent as **application/json**."
        ),
        request_body=HomeOwnerCreateSerializer,
        responses={
            201: openapi.Response(
                description="Home owner created successfully",
                schema=HomeOwnerSerializer
            ),
            400: ValidationErrorResponse,
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        homeowner = serializer.save()
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "data": HomeOwnerSerializer(homeowner, context={'request': request}).data,
            "message": "Home owner registered and QBox linked successfully"
        }, status=status.HTTP_201_CREATED)

class HomeOwnerDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single home owner
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get home owner details",
            description="Retrieve detailed information about a specific home owner including personal info and current status.",
            serializer=HomeOwnerSerializer
        )
    )
    def get(self, request, *args, **kwargs):
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
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update home owner",
            description="Update home owner information such as name, phone, or active status.",
            serializer=HomeOwnerSerializer
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
            "message": "Home Owner updated successfully"
        }, status=status.HTTP_200_OK)


class HomeOwnerStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update home owner active status
    '''
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerStatusUpdateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Home Owner] Update home owner status",
        operation_description="Update home owner active status. Activating a home owner enables their account access. Deactivating temporarily suspends their access.",
        tags=["Home Owner"],
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
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete home owner",
            description="Remove a home owner from the system. This action is permanent and cannot be undone."
        )
    )
    def delete(self, request, *args, **kwargs):
        home_owner = self.get_object()
        home_owner_data = HomeOwnerSerializer(home_owner).data
        home_owner.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": home_owner_data,
            "message": "Home Owner deleted successfully"
        }, status=status.HTTP_200_OK)


class HomeOwnerLoginView(generics.CreateAPIView):
    """
    Login for home owner with email or phone number
    """
    serializer_class = HomeOwnerLoginSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Home Owner Login",
            description="Authenticate home owner with email or phone number and password to receive JWT tokens.",
            serializer=HomeOwnerLoginSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        from rest_framework_simplejwt.tokens import RefreshToken
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": HomeOwnerSerializer(user).data
                },
                "message": "Login successful"
            }, status=status.HTTP_200_OK)


class HomeOwnerResetPasswordView(generics.CreateAPIView):
    """
    Reset password for home owner with email and new password
    """
    serializer_class = HomeOwnerResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Reset Home Owner Password",
            description="Reset the password for a home owner using their email and new password.",
            serializer=HomeOwnerResetPasswordSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": None,
            "message": "Password reset successfully"
            
        }, status=status.HTTP_200_OK)
