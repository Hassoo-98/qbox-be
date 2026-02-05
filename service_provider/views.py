from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ServiceProvider
from .serializers import ServiceProviderSerializer, ServiceProviderApprovalSerializer
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

# Swagger Helper for Service Provider
swagger = SwaggerHelper(tag="Service Provider")


class ServiceProviderListCreateView(APIView):
    """
    GET: List all service providers
    POST: Create a new service provider
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all service providers",
            description="Retrieve a list of all service providers registered in the system with their business details, approval status, and operating cities.",
            serializer=ServiceProviderSerializer
        )
    )
    def get(self, request):
        service_providers = ServiceProvider.objects.all()
        serializer = ServiceProviderSerializer(service_providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new service provider",
            description="Register a new service provider with business registration, contact details, operating cities, and pricing configuration.",
            serializer=ServiceProviderSerializer
        )
    )
    def post(self, request):
        serializer = ServiceProviderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceProviderDetailView(APIView):
    """
    GET: Retrieve a single service provider
    DELETE: Delete a service provider
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get a single service provider",
            description="Retrieve detailed information about a specific service provider including business details, operating schedule, and approval status.",
            serializer=ServiceProviderSerializer
        )
    )
    def get(self, request, pk):
        try:
            service_provider = ServiceProvider.objects.get(pk=pk)
        except ServiceProvider.DoesNotExist:
            return Response(
                {"error": "Service provider not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ServiceProviderSerializer(service_provider)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete a service provider",
            description="Remove a service provider from the system. This action is permanent and cannot be undone."
        )
    )
    def delete(self, request, pk):
        try:
            service_provider = ServiceProvider.objects.get(pk=pk)
        except ServiceProvider.DoesNotExist:
            return Response(
                {"error": "Service provider not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        service_provider.delete()
        return Response(
            {"message": "Service provider deleted successfully"},
            status=status.HTTP_200_OK
        )


class ServiceProviderApprovalView(APIView):
    """
    PATCH: Approve or disapprove a service provider
    URL parameter: id in URL
    Payload: is_approved (boolean)
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Service Provider] Approve or disapprove a service provider",
        operation_description="Update the approval status of a service provider. When is_approved is set to true, the provider can start operating. Setting it to false revokes their access.",
        tags=["Service Provider"],
        responses={
            200: openapi.Response(
                description="Service provider approval status updated successfully",
                schema=create_success_response(
                    get_serializer_schema(ServiceProviderSerializer),
                    description="Approval status updated"
                ).schema
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
        }
    )
    def patch(self, request, pk):
        try:
            service_provider = ServiceProvider.objects.get(pk=pk)
        except ServiceProvider.DoesNotExist:
            return Response(
                {"error": "Service provider not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ServiceProviderApprovalSerializer(data=request.data)
        if serializer.is_valid():
            service_provider.is_approved = serializer.validated_data['is_approved']
            service_provider.save()
            response_serializer = ServiceProviderSerializer(service_provider)
            return Response(
                {
                    "message": f"Service provider {'approved' if service_provider.is_approved else 'disapproved'} successfully",
                    "data": response_serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
