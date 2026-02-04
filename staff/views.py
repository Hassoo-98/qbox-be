from urllib import request
from venv import logger
from rest_framework import generics, status, filters
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import CustomStaff
from .serializers import (
    StaffSerializer,
    StaffCreateSerializer,
    StaffStatusUpdateSerializer,
    StaffUpdateSerializer
)

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'  
    max_page_size = 100
    page_query_param = 'page'


class StaffListAPIView(generics.ListAPIView):
    """
    GET: List all staff members with paginated response in custom format
    
    """
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'email', 'phone_number']           
    ordering_fields = ['name', 'email', 'role', 'date_joined']
    ordering = ['-date_joined']                                
    filterset_fields = ['role', 'is_active']                    

    def get_paginated_response(self, data):
        """
        Override to return your exact custom format
        This method is called automatically when pagination is active
        """
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
            "message": "List users"
        })

    def list(self, request, *args, **kwargs):
        """
        We override list() mainly to handle the non-paginated fallback case
        """
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
                "total": queryset.count(),
                "page": 1,
                "limit": queryset.count() if queryset.exists() else 0,
                "hasMore": False,
            },
            "message": "List users"
        })






class StaffCreateAPIView(generics.CreateAPIView):
    """
    POST: Create a new staff member
    """
    queryset = CustomStaff.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        
        return Response({
            "success": True,
            "statusCode": 201,
            "message": "Staff member created successfully",
            "data": {
                "id": staff.id,
                "name": staff.name,
                "email": staff.email,
                "phone_number": staff.phone_number,
                "role": staff.role,
                "is_active": staff.is_active,
                "is_staff": staff.is_staff,
                "date_joined": staff.date_joined
            }
        }, status=status.HTTP_201_CREATED)

class StaffUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomStaff.objects.all()
    serializer_class = StaffUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        serializer=self.get_serializer(instance)
        staff=serializer.data

        return Response({
            "success":True,
            "statusCode":status.HTTP_200_OK,
            "data":{
             "name":staff["name"],
             "email":staff["email"],
             "phone_number":staff["phone_number"],
             "role":staff["role"],
             "is_active":staff["is_active"],

            },
            "message":"Staff updated successfully"
        },status=status.HTTP_200_OK)

    

class StaffChangeStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        staff = get_object_or_404(CustomStaff, id=id)

        serializer = StaffStatusUpdateSerializer(staff, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        updated_staff =StaffSerializer(staff).data
        status_text = "activated" if serializer.validated_data['is_active'] else "deactivated"
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": f"Staff member {staff.email} has been {status_text}.",
            "data": updated_staff
        }, status=status.HTTP_200_OK)

class StaffDeleteAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,id):
        staff=get_object_or_404(CustomStaff,id=id)
        if staff.role=="supervisor":
            active_supervisors=CustomStaff.objects.filter(
                role="supervisor",is_active=True
            ).exclude(id=staff.id).count()
            if active_supervisors==0:
                return Response({
                    "success":False,
                    "statusCode":status.HTTP_400_BAD_REQUEST,
                    "message":"At least one active supervisor is required. Cannot delete the last active supervisor.",
                },status=status.HTTP_400_BAD_REQUEST)
        email=staff.email
        staff_id=staff.id
        staff.delete()
        logger.info(f"Staff member {email} (ID: {id}) was deleted by {request.user.email if request.user.is_authenticated else 'system'}")
        return Response({  
            "success":True,
            "statusCode":status.HTTP_200_OK,
            "data":{
                "id":staff_id,
                "name":staff.name,
                "email":staff.email,
                "phone_number":staff.phone_number,
                "role":staff.role,
                "is_active":staff.is_active
            },
            "message": f"Staff member {email} has been successfully deleted."
        },status=status.HTTP_200_OK)
class StaffDetailAPIView(generics.RetrieveAPIView): 
    """
    GET: Retrieve a single staff member by ID
    """
    queryset = CustomStaff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Staff"
        }, status=status.HTTP_200_OK)