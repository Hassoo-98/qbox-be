from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Qbox
from .serializers import QboxSerializer, QboxListSerializer, QboxCreateSerializer, QboxUpdateSerializer

class QboxListAPIView(generics.ListAPIView):
    """
    GET: List all qboxes
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxListSerializer
    permission_classes = [IsAuthenticated]

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
            "message": "Qbox List"
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
                "hasMore": False
            },
            "message": "Qbox List"
        })

class QboxDetailAPIView(generics.RetrieveAPIView):
    """
    GET: Get qbox details by ID
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Qbox Details"
        })

class QboxByIdAPIView(generics.RetrieveAPIView):
    """
    GET: Get qbox details by qbox_id
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "qbox_id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Qbox Details"
        })

class QboxCreateAPIView(generics.CreateAPIView):
    """
    POST: Create a new qbox
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qbox = serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_201_CREATED,
            "data": QboxSerializer(qbox).data,
            "message": "Qbox created successfully"
        }, status=status.HTTP_201_CREATED)

class QboxUpdateAPIView(generics.UpdateAPIView):
    """
    PUT/PATCH: Update qbox
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        qbox = serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": QboxSerializer(qbox).data,
            "message": "Qbox updated successfully"
        })

class QboxDeleteAPIView(generics.DestroyAPIView):
    """
    DELETE: Delete qbox
    """
    queryset = Qbox.objects.all()
    serializer_class = QboxSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = QboxSerializer(instance).data
        instance.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": data,
            "message": "Qbox deleted successfully"
        })
