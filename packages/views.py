from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Package
from .serializers import (
    PackageSerializer,
    PackageCreateSerializer,
    PackageStatusUpdateSerializer,
    PackageUpdateSerializer,
    SendPackageSerializer,
    ReturnPackageSerializer,
    OutgoingPackageSerializer,
)
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

swagger = SwaggerHelper(tag="Package")



package_type_schema = openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=Package.PackageType.values,
    description="Package type: 'Incoming', 'Outgoing', or 'Delivered'"
)


outgoing_status_schema = openapi.Schema(
    type=openapi.TYPE_STRING,
    enum=Package.OutgoingStatus.values,
    description="Outgoing status: 'Sent' or 'Return' (only for Outgoing packages)"
)


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


class PackageListAPIView(generics.ListAPIView):
    '''
    Get: List all packages with pagination and filters
    
    Query Parameters:
    - search: Search by tracking_id, merchant_name, service_provider, driver_name
    - ordering: Order by field (tracking_id, merchant_name, service_provider, driver_name, created_at, last_update, package_type, shipment_status)
    - package_type: Filter by package type (Incoming, Outgoing, Delivered)
    - outgoing_status: Filter by outgoing status (Sent, Return) - only applicable for Outgoing packages
    '''
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, filters.BaseFilterBackend]
    search_fields = ["tracking_id", "merchant_name", "service_provider", "driver_name"]
    ordering_fields = ["tracking_id", "merchant_name", "service_provider", "driver_name", "created_at", "last_update", "package_type", "shipment_status"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by package_type
        package_type = self.request.query_params.get('package_type')
        if package_type:
            queryset = queryset.filter(package_type=package_type)
        
        # Filter by outgoing_status (only for Outgoing packages)
        outgoing_status = self.request.query_params.get('outgoing_status')
        if outgoing_status:
            queryset = queryset.filter(outgoing_status=outgoing_status)
        
        return queryset
    
    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all packages",
            description="Retrieve a paginated list of all packages with optional filtering by search query, ordering, package type, and outgoing status.",
            serializer=PackageSerializer
        ),
        manual_parameters=[
            openapi.Parameter(
                'package_type',
                openapi.IN_QUERY,
                description="Filter by package type (Incoming, Outgoing, Delivered)",
                type=openapi.TYPE_STRING,
                enum=Package.PackageType.choices
            ),
            openapi.Parameter(
                'outgoing_status',
                openapi.IN_QUERY,
                description="Filter by outgoing status (Sent, Return) - only for Outgoing packages",
                type=openapi.TYPE_STRING,
                enum=Package.OutgoingStatus.choices
            ),
        ]
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
            "message": "List Packages"
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


class PackageCreateAPIView(generics.CreateAPIView):
    '''
    Post: Create a new package
    
    Package Types:
    - **Incoming**: For packages being delivered TO a location. Requires 'city' field.
    - **Outgoing**: For packages being sent FROM a location. Requires 'outgoing_status' field (Sent or Return).
    - **Delivered**: For packages that have been delivered. No special requirements.
    
    Field Requirements by Package Type:
    - Incoming: city (required), outgoing_status (not allowed)
    - Outgoing: outgoing_status (required: Sent or Return), city (optional)
    - Delivered: no special requirements
    '''
    queryset = Package.objects.all()
    serializer_class = PackageCreateSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new package",
            description="Register a new package. Package type determines field requirements: Incoming requires city, Outgoing requires outgoing_status.",
            serializer=PackageCreateSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                package = serializer.save()
                package_data = PackageSerializer(package).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": package_data,
                    "message": "Package created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PackageDetailAPIView(generics.RetrieveAPIView):
    '''
    Get: Retrieve a single package
    '''
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get package details",
            description="Retrieve detailed information about a specific package including all fields and status.",
            serializer=PackageSerializer
        )
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data,
            "message": "Get Package"
        }, status=status.HTTP_200_OK)


class PackageUpdateAPIView(generics.UpdateAPIView):
    '''
    Put/Patch: Update a package
    
    Package Types:
    - **Incoming**: Requires 'city' field, 'outgoing_status' not allowed
    - **Outgoing**: Requires 'outgoing_status' field (Sent or Return)
    - **Delivered**: No special requirements
    
    Field Requirements by Package Type:
    - Incoming: city (required), outgoing_status (not allowed)
    - Outgoing: outgoing_status (required: Sent or Return), city (optional)
    - Delivered: no special requirements
    '''
    queryset = Package.objects.all()
    serializer_class = PackageUpdateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update package",
            description="Update package information. Package type determines field requirements.",
            serializer=PackageUpdateSerializer
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
            "message": "Package updated successfully"
        }, status=status.HTTP_200_OK)


class PackageStatusUpdateAPIView(generics.UpdateAPIView):
    '''
    Patch: Update package type and status
    
    Updates package type with validation:
    - **Incoming**: Requires 'city', 'outgoing_status' not allowed
    - **Outgoing**: Requires 'outgoing_status' (Sent or Return)
    - **Delivered**: No special requirements
    '''
    queryset = Package.objects.all()
    serializer_class = PackageStatusUpdateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Package] Update package type and status",
        operation_description="Update package type with conditional field validation based on package type.",
        tags=["Package"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["package_type", "is_active"],
            properties={
                "package_type": package_type_schema,
                "outgoing_status": outgoing_status_schema,
                "city": openapi.Schema(type=openapi.TYPE_STRING, description="City name (required for Incoming)"),
                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Active status")
            }
        ),
        responses={
            200: create_success_response(
                get_serializer_schema(PackageSerializer),
                description="Package status updated successfully"
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
            "data": PackageSerializer(serializer.instance).data,
            "message": "Package status updated successfully"
        }, status=status.HTTP_200_OK)


class PackageDeleteAPIView(generics.DestroyAPIView):
    '''
    Delete: Remove a package
    '''
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete package",
            description="Remove a package from the system. This action is permanent and cannot be undone."
        )
    )
    def delete(self, request, *args, **kwargs):
        package = self.get_object()
        package_data = PackageSerializer(package).data
        package.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": package_data,
            "message": "Package deleted successfully"
        }, status=status.HTTP_200_OK)


class SendPackageAPIView(generics.CreateAPIView):
    '''
    Post: Create a new send package (outgoing package with 'Sent' status)
    
    This endpoint creates an outgoing package with outgoing_status set to 'Sent'.
    The package will be of type 'Outgoing' and can be filtered using package_type=Outgoing
    with outgoing_status=Sent in the packages list API.
    
    Request Body (camelCase field names - ALL FIELDS REQUIRED):
    {
        "shippingCompany": "mainDoor",
        "qboxImage": "file:///data/user/0/host.exp.exponent/cache/ImagePicker/390808c2-8678-47cb-9502-dd7661e11b33.jpeg",
        "packageDescription": "This is the description",
        "packageItemValue": 5,
        "currency": "sar",
        "packageWeight": 2,
        "packageType": "mainDoor",
        "qBoxId": "345345",
        "phone": "+923434534533",
        "email": "sardar@gmail.com",
        "fullName": "Sardar Hussain"
    }
    
    Response:
    {
        "success": true,
        "statusCode": 201,
        "data": {
            "id": "uuid",
            "tracking_id": "SND-ABC12345",
            "merchant_name": "Sardar Hussain",
            "service_provider": "mainDoor",
            "outgoing_status": "Sent",
            "package_type": "Outgoing",
            "shipment_status": "Shipment-Created",
            ...
        },
        "message": "Send package created successfully"
    }
    '''
    queryset = Package.objects.all()
    serializer_class = SendPackageSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="[Package] Create send package",
        operation_description="""Create a new outgoing package with 'Sent' status.
        
        This endpoint is used to send a package from a QBox location. The package will:
        - Have package_type set to 'Outgoing'
        - Have outgoing_status set to 'Sent'
        - Be retrievable via the main packages list API with ?package_type=Outgoing&outgoing_status=Sent
        
        ALL FIELDS ARE REQUIRED as per the API specification.
        """,
        tags=["Package"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["shippingCompany", "qboxImage", "packageDescription", "packageItemValue", 
                      "currency", "packageWeight", "packageType", "qBoxId", "phone", "email", "fullName"],
            properties={
                "shippingCompany": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Shipping company name",
                    example="mainDoor"
                ),
                "qboxImage": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="URL or file path of the package image",
                    example="file:///data/user/0/host.exp.exponent/cache/ImagePicker/390808c2-8678-47cb-9502-dd7661e11b33.jpeg"
                ),
                "packageDescription": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Description of the package",
                    example="This is the description"
                ),
                "packageItemValue": openapi.Schema(
                    type=openapi.TYPE_NUMBER, 
                    description="Value of the package item",
                    example=5
                ),
                "currency": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Currency code (e.g., SAR, USD)",
                    example="sar"
                ),
                "packageWeight": openapi.Schema(
                    type=openapi.TYPE_NUMBER, 
                    description="Weight of the package",
                    example=2
                ),
                "packageType": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Type of package",
                    example="mainDoor"
                ),
                "qBoxId": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="QBox ID",
                    example="345345"
                ),
                "phone": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Contact phone number",
                    example="+923434534533"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    format=openapi.FORMAT_EMAIL, 
                    description="Contact email",
                    example="sardar@gmail.com"
                ),
                "fullName": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Full name of the sender",
                    example="Sardar Hussain"
                ),
            }
        ),
        responses={
            201: create_success_response(
                get_serializer_schema(PackageSerializer),
                description="Send package created successfully. Returns the created package with tracking ID."
            ),
            400: ValidationErrorResponse,
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                package = serializer.save()
                package_data = PackageSerializer(package).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": package_data,
                    "message": "Send package created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ReturnPackageAPIView(generics.CreateAPIView):
    '''
    Post: Create a new return package (outgoing package with 'Return' status)
    
    This endpoint creates an outgoing package with outgoing_status set to 'Return'.
    The package will be of type 'Outgoing' and can be filtered using package_type=Outgoing
    with outgoing_status=Return in the packages list API.
    
    Request Body (camelCase field names - ALL FIELDS REQUIRED):
    {
        "returnPackageImage": "file:///data/user/0/host.exp.exponent/cache/ImagePicker/124282a4-d02b-40f6-a767-fba00bbddc42.jpeg",
        "packageDescription": "This is the description for the return package",
        "packageItemValue": 8,
        "currency": "sar",
        "packageWeight": 3,
        "packageType": "mainDoor",
        "pinCode": "1231"
    }
    
    Response:
    {
        "success": true,
        "statusCode": 201,
        "data": {
            "id": "uuid",
            "tracking_id": "RET-ABC12345",
            "outgoing_status": "Return",
            "package_type": "Outgoing",
            "shipment_status": "Shipment-Created",
            ...
        },
        "message": "Return package created successfully"
    }
    '''
    queryset = Package.objects.all()
    serializer_class = ReturnPackageSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="[Package] Create return package",
        operation_description="""Create a new outgoing package with 'Return' status.
        
        This endpoint is used to return a package to a QBox location. The package will:
        - Have package_type set to 'Outgoing'
        - Have outgoing_status set to 'Return'
        - Be retrievable via the main packages list API with ?package_type=Outgoing&outgoing_status=Return
        
        ALL FIELDS ARE REQUIRED as per the API specification.
        """,
        tags=["Package"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["returnPackageImage", "packageDescription", "packageItemValue", 
                      "currency", "packageWeight", "packageType", "pinCode"],
            properties={
                "returnPackageImage": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="URL or file path of the return package image",
                    example="file:///data/user/0/host.exp.exponent/cache/ImagePicker/124282a4-d02b-40f6-a767-fba00bbddc42.jpeg"
                ),
                "packageDescription": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Description of the return package",
                    example="This is the description for the return package"
                ),
                "packageItemValue": openapi.Schema(
                    type=openapi.TYPE_NUMBER, 
                    description="Value of the package item",
                    example=8
                ),
                "currency": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Currency code (e.g., SAR, USD)",
                    example="sar"
                ),
                "packageWeight": openapi.Schema(
                    type=openapi.TYPE_NUMBER, 
                    description="Weight of the package",
                    example=3
                ),
                "packageType": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Type of package",
                    example="mainDoor"
                ),
                "pinCode": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="PIN code for return",
                    example="1231"
                ),
            }
        ),
        responses={
            201: create_success_response(
                get_serializer_schema(PackageSerializer),
                description="Return package created successfully. Returns the created package with tracking ID."
            ),
            400: ValidationErrorResponse,
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                package = serializer.save()
                package_data = PackageSerializer(package).data
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_201_CREATED,
                    "data": package_data,
                    "message": "Return package created successfully"
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class OutgoingPackagesAPIView(generics.ListAPIView):
    '''
    Get: List all outgoing packages (includes both Send and Return packages)
    
    This endpoint retrieves all packages with package_type='Outgoing', which includes:
    - Send packages (outgoing_status='Sent')
    - Return packages (outgoing_status='Return')
    
    Query Parameters:
    - search: Search by tracking_id, service_provider, outgoing_status
    - ordering: Order by field (tracking_id, created_at, last_update, shipment_status)
    - outgoing_status: Filter by outgoing status (Sent or Return)
    '''
    queryset = Package.objects.filter(package_type='Outgoing')
    serializer_class = OutgoingPackageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tracking_id', 'service_provider', 'outgoing_status', 'merchant_name']
    ordering_fields = ['tracking_id', 'created_at', 'last_update', 'shipment_status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by outgoing_status (Sent or Return)
        outgoing_status = self.request.query_params.get('outgoing_status')
        if outgoing_status:
            queryset = queryset.filter(outgoing_status=outgoing_status)
        
        return queryset
    
    @swagger_auto_schema(
        operation_summary="[Package] List outgoing packages",
        operation_description="""Retrieve a paginated list of all outgoing packages.
        
        This includes both:
        - Send packages (outgoing_status='Sent') - created via POST /packages/send
        - Return packages (outgoing_status='Return') - created via POST /packages/return
        
        Filter by outgoing_status to get only Send or Return packages.
        """,
        tags=["Package"],
        manual_parameters=[
            openapi.Parameter(
                'outgoing_status',
                openapi.IN_QUERY,
                description="Filter by outgoing status (Sent, Return)",
                type=openapi.TYPE_STRING,
                enum=Package.OutgoingStatus.choices
            ),
        ],
        responses={
            200: create_success_response(
                get_serializer_schema(OutgoingPackageSerializer, many=True),
                description="Outgoing packages retrieved successfully. Returns list of all outgoing packages."
            ),
        }
    )
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
            },
            "message": "Outgoing packages retrieved successfully"
        })


class DeliveredPackagesAPIView(generics.ListAPIView):
    '''
    Get: List all delivered packages
    '''
    queryset = Package.objects.filter(package_type='Delivered')
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tracking_id', 'merchant_name', 'service_provider', 'driver_name']
    ordering_fields = ['tracking_id', 'merchant_name', 'service_provider', 'driver_name', 'created_at', 'last_update']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_summary="[Package] List delivered packages",
        operation_description="Retrieve a paginated list of all delivered packages",
        tags=["Package"],
        responses={
            200: create_success_response(
                get_serializer_schema(PackageSerializer, many=True),
                description="Delivered packages retrieved successfully"
            ),
        }
    )
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
            },
            "message": "Delivered packages retrieved successfully"
        })


class IncomingPackagesAPIView(generics.ListAPIView):
    '''
    Get: List all incoming packages
    '''
    queryset = Package.objects.filter(package_type='Incoming')
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tracking_id', 'merchant_name', 'service_provider', 'driver_name', 'city']
    ordering_fields = ['tracking_id', 'merchant_name', 'service_provider', 'driver_name', 'city', 'created_at', 'last_update']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_summary="[Package] List incoming packages",
        operation_description="Retrieve a paginated list of all incoming packages",
        tags=["Package"],
        responses={
            200: create_success_response(
                get_serializer_schema(PackageSerializer, many=True),
                description="Incoming packages retrieved successfully"
            ),
        }
    )
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
            },
            "message": "Incoming packages retrieved successfully"
        })
