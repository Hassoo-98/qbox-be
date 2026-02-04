from typing import override
from django.shortcuts import render
from venv import logger
from rest_framework import generics,status,filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import CustomDriver
from .serializers import (
    DriverSerializer,
    DriverCreateSerializer,
    DriverStatusUpdateSerializer,
    DriverUpdateSerializer
)
class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"

class DriverListAPIView(generics.ListAPIView):
    '''
    Get: list all drivers with pagination and filters
    '''
    queryset = CustomDriver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "email", "phone_number"]
    ordering_fields = ["name", "email", "phone_number"]
    ordering = ["-date_joined"]
    filterset_fields = ["is_active"]

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
            "message": "List Drivers"
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

class DriverCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new driver
    '''
    queryset = CustomDriver.objects.all()
    serializer_class = DriverCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                driver = serializer.save()
                driver_data = DriverSerializer(driver).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": driver_data,
                    "message": "Driver created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DriverUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomDriver.objects.all()
    serializer_class = DriverUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
                "message": "Driver updated successfully"
            }, status=status.HTTP_200_OK)

class DriverStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomDriver.objects.all()
    serializer_class = DriverStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch'] 

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
            "data": DriverSerializer(serializer.instance).data,
            "message": "Driver status updated successfully"
        }, status=status.HTTP_200_OK)

class DriverDeleteAPIView(generics.DestroyAPIView):
    queryset = CustomDriver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        driver = self.get_object()
        driver_data = DriverSerializer(driver).data
        driver.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": driver_data,
            "message": "Driver deleted successfully"
        }, status=status.HTTP_200_OK)

class DriverDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomDriver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Driver"
        }, status=status.HTTP_200_OK)
