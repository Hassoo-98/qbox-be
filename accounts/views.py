from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status, permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    OTPSerializer
)
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

# Swagger Helper for Authentication
swagger = SwaggerHelper(tag="Authentication")


class RegisterView(generics.CreateAPIView):
    """
    Register a new user (home owner, driver, staff, or service provider)
    """
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Register a new user",
            description="Register a new user with email, password, and role selection. The user will receive a verification email.",
            serializer=RegisterSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # Generate verification token
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send verification email
            subject = 'Verify your email'
            message = render_to_string('verification_email.html', {
                'user': user,
                'uidb64': uidb64,
                'token': token,
            })
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception as e:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "data": None,
                    "message": f"User created but failed to send verification email: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "success": True,
                "statusCode": status.HTTP_201_CREATED,
                "data": UserSerializer(user).data,
                "message": "User registered successfully. Please check your email to verify your account."
            }, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    """
    Login and get JWT tokens
    """
    queryset = CustomUser.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Login user",
            description="Authenticate user with email and password to receive JWT access and refresh tokens.",
            serializer=LoginSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data
                },
                "message": "Login successful"
            }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user's profile
    """
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get current user profile",
            description="Retrieve the profile information of the currently authenticated user.",
            serializer=UserProfileSerializer
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update current user profile",
            description="Update the profile information of the currently authenticated user.",
            serializer=UserProfileSerializer
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Partial update current user profile",
            description="Partially update the profile information of the currently authenticated user.",
            serializer=UserProfileSerializer
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change current user's password
    """
    serializer_class = ChangePasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Change password",
            description="Change the password of the currently authenticated user. Requires current password for verification.",
            serializer=ChangePasswordSerializer
        )
    )
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": None,
            "message": "Password changed successfully"
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.CreateAPIView):
    """
    Request password reset email
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Request password reset",
            description="Request a password reset email. If the email exists in the system, a reset link will be sent.",
            serializer=PasswordResetRequestSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            subject = 'Password Reset Request'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'uidb64': uidb64,
                'token': token,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        except CustomUser.DoesNotExist:
            pass  # Don't reveal if user exists
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": None,
            "message": "If an account exists with this email, a password reset link has been sent."
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.CreateAPIView):
    """
    Confirm password reset with new password
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Confirm password reset",
            description="Reset the user's password using the token sent to their email.",
            serializer=PasswordResetConfirmSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": None,
            "message": "Password has been reset successfully"
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (admin only)
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'list', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @swagger_auto_schema(
        **swagger.list_operation(
            summary="List all users",
            description="Retrieve a list of all users (admin only). Regular users can only see their own profile.",
            serializer=UserSerializer
        )
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        **swagger.retrieve_operation(
            summary="Get user details",
            description="Retrieve detailed information about a specific user.",
            serializer=UserSerializer
        )
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Create a new user",
            description="Create a new user account (admin only).",
            serializer=UserSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Update user",
            description="Update user information (admin only or self).",
            serializer=UserSerializer
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        **swagger.delete_operation(
            summary="Delete user",
            description="Remove a user from the system (admin only). This action is permanent and cannot be undone."
        )
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class VerifyEmailView(APIView):
    """
    Verify user email with token
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify email",
        operation_description="Verify user email using the token sent to their email address.",
        tags=["Authentication"],
        manual_parameters=[
            openapi.Parameter(
                'uidb64',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Base64 encoded user ID'
            ),
            openapi.Parameter(
                'token',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Verification token'
            )
        ],
        responses={
            200: create_success_response(
                openapi.Schema(type=openapi.TYPE_OBJECT),
                description="Email verified successfully"
            ),
            400: ValidationErrorResponse,
        }
    )
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.email_verified = True
                user.save()
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": None,
                    "message": "Email verified successfully"
                }, status=status.HTTP_200_OK)
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "Invalid or expired token"
            }, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "Invalid user"
            }, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(generics.CreateAPIView):
    """
    Verify user with OTP sent to email
    """
    serializer_class = OTPSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Verify OTP",
            description="Verify user email using the OTP sent to their email address.",
            serializer=OTPSerializer
        )
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": None,
            "message": "OTP verified successfully"
        }, status=status.HTTP_200_OK)
