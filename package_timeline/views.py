from rest_framework import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PackageTimeline
from .serializers import PackageTimelineSerializer
from rest_framework import permissions as permission
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from utils.swagger_schema import SwaggerHelper,get_serializer_schema
swagger=SwaggerHelper("Package Timeline")
class StandardResultsSetPagination(PageNumberPagination):
    page_size=10
    page_size_query_param="page_size"
    max_page_size=100


# ===========================
# LIST + CREATE
# ===========================

class PackageTimeListItemView(APIView):
    """
    GET: Get all package timelines
    POST: Create new timeline entry
    """
    permission_classes=[permission.AllowAny]
    pagination_class=StandardResultsSetPagination
    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List Package Timelines",
            serializer=PackageTimelineSerializer
        )
    )

    def get(self,request):
        timelines=PackageTimeline.objects.all().order_by("-id")
        paginator=self.pagination_class()
        paginated_qs = paginator.paginate_queryset(timelines, request)
        serializer = PackageTimelineSerializer(paginated_qs, many=True)
        return Response({
            "success":True,
            "statusCode":status.HTTP_200_OK,
            "data":{
                "items":serializer.data,
                "total":paginator.page.paginator.count,
                "limit":paginator.page.paginator.per_page,
                "hasMore":paginator.page.has_next()
            }
        },status=status.HTTP_200_OK)
    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create Package Timeline",
            serializer=PackageTimelineSerializer
        )
    )
    def post(self,request):
        serializer=PackageTimelineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success":True,
                "statusCode":status.HTTP_201_CREATED,
                "data":serializer.data,
                "message":"Timeline successfully created"
            },status=status.HTTP_201_CREATED)
        return Response({
            "success":False,
            "statusCode":status.HTTP_400_BAD_REQUEST,
            "data":serializer.errors,
            "message":"validation error"
        })

class PackageTimelineDetailView(APIView):
    """
    GET: Retrieve single timeline
    DELETE: Delete timeline
    """
    permission_classes=[permission.AllowAny]
    def get_object(self,request,pk):
        return get_object_or_404(PackageTimeline,pk=pk)
    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Retrieve Package Timeline",
            serializer=PackageTimelineSerializer
        )
    )
    def get(self,request,pk):
        timeline=self.get_object(pk)
        serializer=PackageTimelineSerializer(timeline)
        return Response({
            "success":True,
            "statusCode":status.HTTP_200_OK,
            "data":serializer.data,
            "message":"Timeline retrieved successfully"
        })
    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete Package Timeline",
            serializer=PackageTimelineSerializer
        )
    )
    def delete(self,request,pk):
        timeline=self.get_object(pk)
        timeline.delete()
        return Response({
            "success":True,
            "statusCode":status.HTTP_200_OK,
            "message":"Timeline deleted successfully"
        },status=status.HTTP_200_OK)

class PackageTimelineByPackageIdView(APIView):
    """
    GET: Retrieve timelines by package ID
    """
    permission_classes=[permission.AllowAny]
    @swagger_auto_schema(
        **swagger.list_operation(
            summary="Get timelines by packageId",
            serializer=PackageTimelineSerializer
        )
    )
    def get(self,request,package_id):
        timelines=PackageTimeline.objects.filter(package_id=package_id)
        
        if not timelines.exists():
            return Response({
                "success":False,
                "statusCode":status.HTTP_404_NOT_FOUND,
                "message":"No timeline found for this package"
            },status=status.HTTP_404_NOT_FOUND)
        serializer=PackageTimelineSerializer(
            timelines,
            many=True
        )
        return Response({
            "success":True,
            "statusCode":status.HTTP_200_OK,
            "data":serializer.data,
            "message":"Package timeline by package Id retrieved successfully"
        },status=status.HTTP_200_OK)
