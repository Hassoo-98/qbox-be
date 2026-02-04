from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import City
from .serializers import CitySerializer

# Swagger Tags
LOCATIONS_TAG = 'Locations'


class CityListCreateView(APIView):
    """
    GET: List all cities
    POST: Create a new city
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="[Locations] List all cities",
        operation_description="Retrieve a list of all cities available in the system. Only returns active cities by default.",
        tags=[LOCATIONS_TAG],
        responses={
            200: CitySerializer(many=True),
            400: "Bad Request",
        }
    )
    def get(self, request):
        cities = City.objects.filter(is_active=True)
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="[Locations] Create a new city",
        operation_description="Add a new city to the system. This city will be available for service providers to select as operating cities.",
        tags=[LOCATIONS_TAG],
        request_body=CitySerializer,
        responses={
            201: CitySerializer,
            400: "Validation errors",
        }
    )
    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CityDetailView(APIView):
    """
    GET: Retrieve a single city
    DELETE: Delete a city
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="[Locations] Get a single city",
        operation_description="Retrieve detailed information about a specific city by ID.",
        tags=[LOCATIONS_TAG],
        responses={
            200: CitySerializer,
            404: "City not found",
        }
    )
    def get(self, request, pk):
        try:
            city = City.objects.get(pk=pk)
        except City.DoesNotExist:
            return Response(
                {"error": "City not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CitySerializer(city)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="[Locations] Delete a city",
        operation_description="Remove a city from the system by ID. This action is permanent and cannot be undone.",
        tags=[LOCATIONS_TAG],
        responses={
            200: "City deleted successfully",
            404: "City not found",
        }
    )
    def delete(self, request, pk):
        try:
            city = City.objects.get(pk=pk)
        except City.DoesNotExist:
            return Response(
                {"error": "City not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        city.delete()
        return Response(
            {"message": "City deleted successfully"},
            status=status.HTTP_200_OK
        )
