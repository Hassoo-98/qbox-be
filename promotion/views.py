from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
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
from utils.swagger_schema import SwaggerHelper,get_serializer_schema
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
        **swagger.create_operation(
            summary="List Promotions",
            serializer=PromotionListSerializer
        )
    )
    def get(self, request):
        promotions = Promotion.objects.all().order_by("-created_at")
        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(promotions, request)
        serializer = PromotionListSerializer(paginated_qs, many=True)
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
        **swagger.create_operation(
            summary="Create Promotion",
            serializer=PromotionSerializer
        )
    )
    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": serializer.data
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
        **swagger.create_operation(
            summary="Get Promotion Detail",
            serializer=PromotionDetailSerializer
        )
    )
    def get(self, request, pk):
        promotion = self.get_object(pk)
        serializer = PromotionDetailSerializer(promotion)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Update Promotion",
            serializer=PromotionSerializer
        )
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
        **swagger.create_operation(
            summary="Delete Promotion",
            serializer=PromotionDeleteSerializer
        )
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
        **swagger.create_operation(
            summary="Update Promotion Status",
            serializer=PromotionStatusSerializer
        )
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
