# home_owner/views.py
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomHomeOwner
from .serializers import (
    HomeOwnerSerializer,
    HomeOwnerCreateSerializer,
    HomeOwnerUpdateSerializer,
    HomeOwnerStatusUpdateSerializer,
    VerifyEmailSerializer,
    VerifyPhoneSerializer,
    VerifyQBoxSerializer,
    VerifyOTPSerializer,
    ForgotPasswordSerializer,
    VerifyForgotPasswordOTPSerializer,
    ResetPasswordSerializer
)
from utils.swagger_schema import (
    ValidationErrorResponse,
    NotFoundResponse,
    ServerErrorResponse,
)

# Swagger Tag
HOME_OWNER_TAG = 'Home Owner'


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    max_page_size = 100
    page_query_param = "page"


class HomeOwnerSignUpAPIView(generics.CreateAPIView):
    """
    POST: Home owner registration (sign up)
    """
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerCreateSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Register new home owner",
        operation_description="Register a new home owner account with name, email, phone, and password.",
        tags=[HOME_OWNER_TAG],
        request_body=HomeOwnerCreateSerializer,
        responses={
            201: openapi.Response(
                description="Home owner registered successfully",
                schema=HomeOwnerSerializer
            ),
            400: ValidationErrorResponse,
            500: ServerErrorResponse,
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            homeowner = serializer.save()
            data = HomeOwnerSerializer(homeowner).data
            return Response({
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": data,
                "message": "Home owner account created successfully. Please verify your email/phone."
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(generics.GenericAPIView):
    """
    POST: Send email verification OTP
    """
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Send email verification OTP",
        operation_description="Send a one-time password (OTP) to the user's email for verification.",
        tags=[HOME_OWNER_TAG],
        request_body=VerifyEmailSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={'otp_key': openapi.Schema(type=openapi.TYPE_STRING)}
                        ),
                    }
                )
            ),
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            otp = CustomHomeOwner.generate_otp()
            user.email_otp = otp
            user.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {"otp_key": otp},
                "message": "OTP sent to your email"
            })
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this email not found"
            })


class VerifyPhoneAPIView(generics.GenericAPIView):
    """
    POST: Send phone verification OTP
    """
    serializer_class = VerifyPhoneSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Send phone verification OTP",
        operation_description="Send a one-time password (OTP) to the user's phone for verification.",
        tags=[HOME_OWNER_TAG],
        request_body=VerifyPhoneSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={'otp_key': openapi.Schema(type=openapi.TYPE_STRING)}
                        ),
                    }
                )
            ),
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        
        try:
            user = CustomHomeOwner.objects.get(phone_number=phone)
            otp = CustomHomeOwner.generate_otp()
            user.phone_otp = otp
            user.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {"otp_key": otp},
                "message": "OTP sent to your phone"
            })
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this phone number not found"
            })


class VerifyOTPAPIView(generics.GenericAPIView):
    """
    POST: Verify OTP for email or phone
    """
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Verify OTP",
        operation_description="Verify the OTP sent for email or phone verification.",
        tags=[HOME_OWNER_TAG],
        request_body=VerifyOTPSerializer,
        responses={
            200: openapi.Response(
                description="OTP verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        verification_type = serializer.validated_data['verification_type']
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            
            if verification_type == 'email':
                if user.email_otp == otp:
                    user.email_verified = True
                    user.email_otp = None
                    user.save()
                    return Response({
                        "success": True,
                        "statusCode": status.HTTP_200_OK,
                        "message": "Email verified successfully"
                    })
                else:
                    return Response({
                        "success": False,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid OTP"
                    })
            
            elif verification_type == 'phone':
                if user.phone_otp == otp:
                    user.phone_verified = True
                    user.phone_otp = None
                    user.save()
                    return Response({
                        "success": True,
                        "statusCode": status.HTTP_200_OK,
                        "message": "Phone number verified successfully"
                    })
                else:
                    return Response({
                        "success": False,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid OTP"
                    })
                    
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this email not found"
            })


class VerifyQBoxAPIView(generics.GenericAPIView):
    serializer_class = VerifyQBoxSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Verify QBox ID",
        operation_description="Verify ownership of a QBox ID associated with the home owner.",
        tags=[HOME_OWNER_TAG],
        request_body=VerifyQBoxSerializer,
        responses={
            200: openapi.Response(
                description="QBox ID verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            403: openapi.Response(description="QBox belongs to another user"),
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qbox_id = serializer.validated_data['qbox_id']
        
        try:
            user = CustomHomeOwner.objects.get(qbox_id=qbox_id)
            if user != request.user:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_403_FORBIDDEN,
                    "message": "This QBox ID belongs to another user"
                })
            user.is_verified = True
            user.save()
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "message": "QBox ID verified successfully"
            })
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "Invalid QBox ID"
            })


class HomeOwnerListAPIView(generics.ListAPIView):
    """
    GET: List all home owners (admin only usually)
    """
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["full_name", "email", "phone_number", "qbox_id"]
    ordering_fields = ["full_name", "date_joined", "is_active"]
    ordering = ["-date_joined"]
    filterset_fields = ["is_active", "is_verified"]

    @swagger_auto_schema(
        operation_summary="[Home Owner] List all home owners",
        operation_description="Retrieve a paginated list of all home owners with filtering options.",
        tags=[HOME_OWNER_TAG],
        responses={
            200: openapi.Response(
                description="Home owners retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            401: openapi.Response(description="Authentication required"),
        }
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
            "message": "Home Owners List"
        })


class HomeOwnerStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomHomeOwner.objects.all()
    serializer_class = HomeOwnerStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    http_method_names = ['patch']

    @swagger_auto_schema(
        operation_summary="[Home Owner] Update home owner status",
        operation_description="Update home owner active status.",
        tags=[HOME_OWNER_TAG],
        request_body=HomeOwnerStatusUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Home owner status updated successfully",
                schema=HomeOwnerSerializer
            ),
            400: ValidationErrorResponse,
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": HomeOwnerSerializer(serializer.instance).data,
            "message": "Home owner status updated successfully"
        })


class HomeOwnerDeleteAPIView(generics.DestroyAPIView):
    queryset = CustomHomeOwner.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    @swagger_auto_schema(
        operation_summary="[Home Owner] Delete home owner",
        operation_description="Remove a home owner account from the system.",
        tags=[HOME_OWNER_TAG],
        responses={
            200: openapi.Response(
                description="Home owner deleted successfully",
                schema=HomeOwnerSerializer
            ),
            401: openapi.Response(description="Authentication required"),
            404: NotFoundResponse,
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        data = HomeOwnerSerializer(instance).data
        instance.delete()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": data,
            "message": "Home owner account deleted successfully"
        })


class ForgotPasswordAPIView(generics.GenericAPIView):
    """
    POST: Send password reset OTP to email or phone
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Send password reset OTP",
        operation_description="Send a password reset OTP to email or phone.",
        tags=[HOME_OWNER_TAG],
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={'otp_key': openapi.Schema(type=openapi.TYPE_STRING)}
                        ),
                    }
                )
            ),
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        send_via = serializer.validated_data.get('send_via', 'email')
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            otp = CustomHomeOwner.generate_otp()
            
            if send_via == 'email':
                user.password_reset_otp = otp
                user.password_reset_otp_expires = timezone.now() + timedelta(minutes=10)
                user.save()
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": {"otp_key": otp},
                    "message": f"Password reset OTP sent to your email"
                })
            elif send_via == 'phone':
                if not user.phone_number:
                    return Response({
                        "success": False,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "message": "No phone number associated with this account"
                    })
                user.password_reset_otp = otp
                user.password_reset_otp_expires = timezone.now() + timedelta(minutes=10)
                user.save()
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": {"otp_key": otp},
                    "message": f"Password reset OTP sent to your phone"
                })
                
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this email not found"
            })


class VerifyForgotPasswordOTPAPIView(generics.GenericAPIView):
    """
    POST: Verify password reset OTP
    """
    serializer_class = VerifyForgotPasswordOTPSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Verify password reset OTP",
        operation_description="Verify the OTP for password reset. OTP expires in 10 minutes.",
        tags=[HOME_OWNER_TAG],
        request_body=VerifyForgotPasswordOTPSerializer,
        responses={
            200: openapi.Response(
                description="OTP verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            
            if (user.password_reset_otp == otp and 
                user.password_reset_otp_expires and 
                user.password_reset_otp_expires > timezone.now()):
                
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "message": "OTP verified successfully. You can now reset your password."
                })
            else:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid or expired OTP"
                })
                
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this email not found"
            })


class ResetPasswordAPIView(generics.GenericAPIView):
    """
    POST: Reset password after OTP verification
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Home Owner] Reset password",
        operation_description="Reset password after OTP verification.",
        tags=[HOME_OWNER_TAG],
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: ValidationErrorResponse,
            404: NotFoundResponse,
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            
            if (user.password_reset_otp == otp and 
                user.password_reset_otp_expires and 
                user.password_reset_otp_expires > timezone.now()):
                
                user.set_password(new_password)
                user.password_reset_otp = None
                user.password_reset_otp_expires = None
                user.save()
                
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "message": "Password reset successfully"
                })
            else:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid or expired OTP"
                })
                
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this email not found"
            })
