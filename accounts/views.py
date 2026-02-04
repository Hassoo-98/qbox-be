from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
import logging
import traceback
import random
import string
import jwt
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .models import CustomUser
logger = logging.getLogger(__name__)
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def generate_otp(length=6):
    """Generate a random 6-digit OTP code."""
    return ''.join(random.choices(string.digits, k=length))


# Swagger Tag
ACCOUNTS_TAG = 'Authentication'


class RegisterView(APIView):
    """Register a new user in the system."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Authentication] Register a new user",
        operation_description="Create a new user account. The user will need to verify their email before they can log in. Required fields: name, email, password, phone_number, role.",
        tags=[ACCOUNTS_TAG],
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'role': openapi.Schema(type=openapi.TYPE_STRING),
                                'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        ),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Validation errors",
            500: "Internal server error",
        }
    )
    def post(self, request):
        logger.info(f"Registration attempt from IP: {request.META.get('REMOTE_ADDR')}")
        logger.debug(f"Request data: {request.data}")

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Registration validation failed: {serializer.errors}")
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = serializer.save()
            logger.info(f"User created successfully: {user.email}")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}\n{traceback.format_exc()}")
            return Response({
                "success": False,
                "statusCode": 500,
                "message": "Error creating user",
                "errors": {"detail": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": True,
            "statusCode": 201,
            "message": "User created successfully. Please verify your email using the OTP.",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "status": user.status,
                "role": user.role,
                "email_verified": user.email_verified
            },
            "createdAt": user.date_joined.isoformat()
        }, status=status.HTTP_201_CREATED)


class VerifyEmailSendOTPView(APIView):
    """Send OTP to user's email for verification (using Django SMTP)."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Authentication] Send email verification OTP",
        operation_description="Send a one-time password (OTP) to the user's email address for email verification. The OTP expires in 10 minutes.",
        tags=[ACCOUNTS_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='The email address to send the verification OTP'
                )
            }
        ),
        responses={
            200: "OTP sent successfully",
            400: "Email is required",
            404: "User not found",
            500: "Failed to send OTP",
        }
    )
    def post(self, request):
        logger.info(f"OTP send request received: {request.data}")
        email = request.data.get('email')

        if not email:
            logger.warning("Email is required but not provided")
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            logger.info(f"User found for OTP: {user.email}")
        except CustomUser.DoesNotExist:
            logger.warning(f"No user found with email: {email}")
            return Response({
                "success": False,
                "statusCode": 404,
                "message": "User with this email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        # Generate and save OTP
        otp = generate_otp()
        logger.info(f"Generated OTP for {email}: {otp}")
        user.verification_token = otp
        user.save(update_fields=['verification_token'])

        # Prepare email content
        subject = "Email Verification OTP - Qbox"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Email Verification</h2>
            <p>Hi {user.name or user.email.split('@')[0]},</p>
            <p>Your one-time password (OTP) for email verification is:</p>
            <h1 style="font-size: 48px; letter-spacing: 10px; color: #333;">{otp}</h1>
            <p>This OTP will expire in <strong>10 minutes</strong>.</p>
            <p style="color: #777; font-size: 14px;">
                If you did not request this, please ignore this email.
            </p>
        </body>
        </html>
        """

        text_content = strip_tags(html_content)

        # Send email using Django SMTP backend
        try:
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@qbox.com'),
                to=[user.email],
            )
            email_message.attach_alternative(html_content, "text/html")

            sent_count = email_message.send(fail_silently=False)
            logger.info(f"OTP email sent successfully to {user.email} | sent_count: {sent_count}")

            return Response({
                "success": True,
                "statusCode": 200,
                "message": "OTP sent successfully to your email. Check your inbox (or Mailtrap dashboard)."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            error_details = str(e)
            if "Authentication" in error_details or "Unauthorized" in error_details:
                error_details += " → Check EMAIL_HOST_USER / EMAIL_HOST_PASSWORD in .env"
            elif "Connection" in error_details:
                error_details += " → Check EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS settings"

            return Response({
                "success": False,
                "statusCode": 500,
                "message": f"Failed to send OTP email: {error_details}",
                "debug_otp": otp   # only for development/testing
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailVerifyOTPView(APIView):
    """Verify the OTP sent to the user."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Authentication] Verify email with OTP",
        operation_description="Verify the user's email address using the OTP sent to their email. This activates the account for login.",
        tags=[ACCOUNTS_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='The email address of the user'
                ),
                'otp': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The 6-digit OTP received in email'
                )
            }
        ),
        responses={
            200: "Email verified successfully",
            400: "Invalid or expired OTP",
            404: "User not found",
        }
    )
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Email and OTP are both required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "statusCode": 404,
                "message": "User with this email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        if user.verification_token != otp:
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Invalid or expired OTP"
            }, status=status.HTTP_400_BAD_REQUEST)

        user.email_verified = True
        user.is_active = True
        user.verification_token = ""  
        user.save(update_fields=['email_verified', 'is_active', 'verification_token'])

        logger.info(f"Email verified successfully for {user.email}")

        return Response({
            "success": True,
            "statusCode": 200,
            "message": "Email verified successfully. You can now log in."
        }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Obtain JWT token pair (access and refresh)."""
    serializer_class = CustomTokenObtainPairSerializer
    
    @swagger_auto_schema(
        operation_summary="[Authentication] Obtain JWT token pair",
        operation_description="Get access and refresh tokens using email and password. Requires email verification first.",
        tags=[ACCOUNTS_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='User email address'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='password',
                    description='User password'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Tokens obtained successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Invalid email or password",
            403: "Email not verified",
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(APIView):
    """Login user and return JWT tokens."""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="[Authentication] Login user",
        operation_description="Authenticate user with email and password. Returns JWT access and refresh tokens along with user information. Requires email verification.",
        tags=[ACCOUNTS_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='User email address'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='password',
                    description='User password'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'statusCode': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'role': openapi.Schema(type=openapi.TYPE_STRING),
                                'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            }
                        ),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'createdAt': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Email and password are required",
            401: "Invalid email or password",
            403: "Email not verified",
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Email and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response({
                "success": False,
                "statusCode": 401,
                "message": "Invalid email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.email_verified:
            return Response({
                "success": False,
                "statusCode": 403,
                "message": "Email is not verified. Please verify your email to proceed."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate simplejwt tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response({
            "success": True,
            "statusCode": 200,
            "message": "Login successful",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "status": user.status,
                "role": user.role,
                "email_verified": user.email_verified,
            },
            "access": access_token,
            "refresh": str(refresh),
            "createdAt": datetime.utcnow().isoformat()
        }, status=status.HTTP_200_OK)

class Forget_PasswordView(APIView):
    """Send OTP to user's email for password reset."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Authentication] Send password reset OTP",
        operation_description="Send a one-time password (OTP) to the user's email for password reset. The OTP expires in 10 minutes.",
        tags=[ACCOUNTS_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='The email address to send the password reset OTP'
                )
            }
        ),
        responses={
            200: "OTP sent successfully",
            400: "Email is required",
            404: "User not found",
            500: "Failed to send OTP",
        }
    )
    def post(self, request):
        logger.info(f"Password reset request received: {request.data}")
        email = request.data.get('email')

        if not email:
            logger.warning("Email is required but not provided")
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            logger.info(f"User found for password reset: {user.email}")
        except CustomUser.DoesNotExist:
            logger.warning(f"No user found with email: {email}")
            return Response({
                "success": False,
                "statusCode": 404,
                "message": "User with this email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        otp = generate_otp()
        logger.info(f"Generated reset OTP for {email}: {otp}")
        user.reset_password_token = otp
        user.save(update_fields=['reset_password_token'])
        subject = "Password Reset OTP - Qbox"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Password Reset Request</h2>
            <p>Hi {user.name or user.email.split('@')[0]},</p>
            <p>You requested to reset your password. Your one-time password (OTP) is:</p>
            <h1 style="font-size: 48px; letter-spacing: 10px; color: #333;">{otp}</h1>
            <p>This OTP will expire in <strong>10 minutes</strong>.</p>
            <p style="color: #777; font-size: 14px;">
                If you did not request a password reset, please ignore this email or contact support.
            </p>
        </body>
        </html>
        """

        text_content = strip_tags(html_content)
        try:
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@qbox.com'),
                to=[user.email],
            )
            email_message.attach_alternative(html_content, "text/html")

            sent_count = email_message.send(fail_silently=False)
            logger.info(f"Password reset OTP sent successfully to {user.email} | sent_count: {sent_count}")

            return Response({
                "success": True,
                "statusCode": 200,
                "message": "Password reset OTP sent successfully to your email. Check your inbox."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Failed to send password reset OTP to {user.email}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            error_details = str(e)
            if "Authentication" in error_details or "Unauthorized" in error_details:
                error_details += " → Check EMAIL_HOST_USER / EMAIL_HOST_PASSWORD in .env"
            elif "Connection" in error_details:
                error_details += " → Check EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS settings"

            return Response({
                "success": False,
                "statusCode": 500,
                "message": f"Failed to send password reset OTP: {error_details}",
                "debug_otp": otp  
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ResetPasswordConfirmView(APIView):
    """Verify OTP and set new password."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="[Authentication] Reset password with OTP",
        operation_description="Verify the OTP sent to the user's email and set a new password. The OTP must match the one sent for password reset.",
        tags=[ACCOUNTS_TAG],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp', 'new_password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='The email address of the user'
                ),
                'otp': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The 6-digit OTP received in email'
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='password',
                    description='The new password to set'
                )
            }
        ),
        responses={
            200: "Password reset successfully",
            400: "Invalid or expired OTP or missing fields",
            404: "User not found",
            500: "Failed to reset password",
        }
    )
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "email, otp, and new_password are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "statusCode": 404,
                "message": "User with this email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        if user.reset_password_token != otp:
            return Response({
                "success": False,
                "statusCode": 400,
                "message": "Invalid or expired OTP"
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.set_password(new_password)
            user.reset_password_token = ""
            user.save(update_fields=['password', 'reset_password_token'])

            logger.info(f"Password reset successful for {user.email}")

            return Response({
                "success": True,
                "statusCode": 200,
                "message": "Password has been reset successfully. You can now log in."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Password reset failed for {email}: {str(e)}")
            return Response({
                "success": False,
                "statusCode": 500,
                "message": f"Failed to reset password: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
