# home_owner/views.py
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            otp = CustomHomeOwner.generate_otp()
            user.email_otp = otp
            user.save()
            # In production, send this OTP via email
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {"otp_key": otp},  # Only for testing/dev
                "message": "OTP sent to your email"
            })
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_404_NOT_FOUND,
                "message": "User with this email not found"
            })


# Similar for phone and qbox — just change field & message
class VerifyPhoneAPIView(generics.GenericAPIView):
    """
    POST: Send phone verification OTP
    """
    serializer_class = VerifyPhoneSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        
        try:
            user = CustomHomeOwner.objects.get(phone_number=phone)
            otp = CustomHomeOwner.generate_otp()
            user.phone_otp = otp
            user.save()
            # In production, send this OTP via SMS
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {"otp_key": otp},  # Only for testing/dev
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
    permission_classes = [IsAuthenticated]           # ← change to custom admin perm if needed
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["full_name", "email", "phone_number", "qbox_id"]
    ordering_fields = ["full_name", "date_joined", "is_active"]
    ordering = ["-date_joined"]
    filterset_fields = ["is_active", "is_verified"]

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
                # In production, send OTP via email
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": {"otp_key": otp},  # Only for testing/dev
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
                # In production, send OTP via SMS
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": {"otp_key": otp},  # Only for testing/dev
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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        send_via = serializer.validated_data.get('send_via', 'email')
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            
            # Check if OTP is valid and not expired
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

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
            
            # Check if OTP is valid and not expired
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
