from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ServiceProvider
from .serializers import ServiceProviderSerializer, ServiceProviderApprovalSerializer

# Swagger Tags
SERVICE_PROVIDER_TAG = 'Service Provider'


class ServiceProviderListCreateView(APIView):
    """
    GET: List all service providers
    POST: Create a new service provider
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="[Service Provider] List all service providers",
        operation_description="Retrieve a list of all service providers registered in the system. Returns detailed information including business registration number, contact details, operating cities, and approval status.",
        tags=[SERVICE_PROVIDER_TAG],
        responses={
            200: ServiceProviderSerializer(many=True),
            400: "Bad Request",
        }
    )
    def get(self, request):
        service_providers = ServiceProvider.objects.all()
        serializer = ServiceProviderSerializer(service_providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="[Service Provider] Create a new service provider",
        operation_description="Register a new service provider in the system with business details including name, business registration number, contact person, phone, email, operating cities, and pricing configuration.",
        tags=[SERVICE_PROVIDER_TAG],
        request_body=ServiceProviderSerializer,
        responses={
            201: ServiceProviderSerializer,
            400: "Validation errors",
        }
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
        operation_summary="[Service Provider] Get a single service provider",
        operation_description="Retrieve detailed information about a specific service provider by ID. Returns all business details, operating schedule, pricing configuration, and approval status.",
        tags=[SERVICE_PROVIDER_TAG],
        responses={
            200: ServiceProviderSerializer,
            404: "Service provider not found",
        }
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
        operation_summary="[Service Provider] Delete a service provider",
        operation_description="Remove a service provider from the system by ID. This action is permanent and cannot be undone.",
        tags=[SERVICE_PROVIDER_TAG],
        responses={
            200: "Service provider deleted successfully",
            404: "Service provider not found",
        }
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
        operation_description="Update the approval status of a service provider. Setting is_approved to true will approve the provider and allow them to operate. Setting it to false will disapprove and revoke their access.",
        tags=[SERVICE_PROVIDER_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['is_approved'],
            properties={
                'is_approved': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Set to true to approve the service provider, false to disapprove'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Service provider approval status updated successfully",
                schema=ServiceProviderSerializer
            ),
            400: "Validation errors",
            404: "Service provider not found",
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
