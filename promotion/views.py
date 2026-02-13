from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.db import models
from django.shortcuts import get_object_or_404
from .models import Promotion
from .serializers import (
    PromotionDeleteSerializer,
    PromotionListSerializer,
    PromotionDetailSerializer,
    PromotionSerializer,
    PromotionStatusSerializer
)
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.swagger_schema import SwaggerHelper, get_serializer_schema
import uuid

swagger = SwaggerHelper("Promotions")


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class PromotionsListView(APIView):
    pagination_class = StandardResultsPagination
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in title, description, or code",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'promo_type',
                openapi.IN_QUERY,
                description="Filter by promo type (Flat or Percentage)",
                type=openapi.TYPE_STRING,
                enum=['Flat', 'Percentage']
            ),
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Filter by active status (true or false)",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'merchant_provider',
                openapi.IN_QUERY,
                description="Filter by merchant provider name",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page (default 10, max 100)",
                type=openapi.TYPE_INTEGER
            ),
        ],
        operation_description="Get a list of all promotions with optional filtering and pagination.",
        responses={
            200: PromotionListSerializer(many=True),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def get(self, request):
        promotions = Promotion.objects.all().order_by("-created_at")
        
        # Filtering params
        search = request.query_params.get('search', None)
        promo_type = request.query_params.get('promo_type', None)
        is_active = request.query_params.get('is_active', None)
        merchant_provider = request.query_params.get('merchant_provider', None)
        
        if search:
            promotions = promotions.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(code__icontains=search)
            )
        
        if promo_type:
            promotions = promotions.filter(promo_type=promo_type)
        
        if is_active is not None:
            promotions = promotions.filter(is_active=is_active.lower() == 'true')
        
        if merchant_provider:
            promotions = promotions.filter(merchant_provider_name__icontains=merchant_provider)
        
        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(promotions, request)
        serializer = PromotionListSerializer(paginated_qs, many=True,context={"request":request})
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                "items": serializer.data,
                "total": paginator.page.paginator.count,
                "limit": paginator.page.paginator.per_page,
                "hasMore": paginator.page.has_next()
            }
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new promotion with optional image URL.",
        request_body=PromotionSerializer,
        responses={
            201: PromotionSerializer,
            400: "Bad Request - Validation errors",
            500: "Internal Server Error"
        }
    )
    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            # Generate unique code in view to avoid multiple calls
            from .models import generate_unique_code
            promotion = serializer.save(code=generate_unique_code())
            return Response({
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": PromotionSerializer(promotion,context={"request":request}).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PromotionDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Promotion, pk=pk)

    @swagger_auto_schema(
        operation_description="Get a single promotion by ID.",
        responses={
            200: PromotionDetailSerializer,
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def get(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionDetailSerializer(promotion,context={"request":request})
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a promotion by ID with optional image URL.",
        request_body=PromotionSerializer,
        responses={
            200: PromotionSerializer,
            400: "Bad Request - Validation errors",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def put(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionSerializer(promotion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a promotion by ID.",
        responses={
            200: "Promotion deleted successfully",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def delete(self, request, pk):
        promotion = self.get_object(pk)
        promotion.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Promotion deleted successfully"
        }, status=status.HTTP_200_OK)


class PromotionStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Promotion, pk=pk)

    @swagger_auto_schema(
        operation_description="Update the active status of a promotion.",
        request_body=PromotionStatusSerializer,
        responses={
            200: PromotionStatusSerializer,
            400: "Bad Request - Validation errors",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def patch(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionStatusSerializer(promotion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
