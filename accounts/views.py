from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from django.http import HttpRequest
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status, permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from core.authentication import CookieJWTAuthentication
from .models import CustomUser
from home_owner.models import CustomHomeOwner
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    OTPSerializer,
    SendOTPSerializer
)
from home_owner.serializers import HomeOwnerSerializer
from utils.swagger_schema import (
    SwaggerHelper,
    get_serializer_schema,
    create_success_response,
    ValidationErrorResponse,
    NotFoundResponse,
    COMMON_RESPONSES,
)

# Get protocol and domain from settings or request
def get_protocol_and_domain(request=None):
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
    else:
        protocol = getattr(settings, 'PROTOCOL', 'http')
        domain = getattr(settings, 'DOMAIN', 'localhost:8000')
    return protocol, domain

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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            protocol, domain = get_protocol_and_domain(request)
            subject = 'Verify your email'
            message = render_to_string('verification_email.html', {
                'user': user,
                'uidb64': uidb64,
                'token': token,
                'protocol': protocol,
                'domain': domain,
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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            role = serializer.validated_data.get('role', None)
            refresh = RefreshToken.for_user(user)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
                  }
            response = Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data": {
                "user": UserSerializer(user).data,
                "tokens": tokens,
                "role": role
            },
            "message": "Login successful"
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite='none',
            max_age=24*60*60
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="none",
            max_age=7*24*60*60
        )
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user's profile
    """
    serializer_class = UserProfileSerializer
    authentication_classes = [CookieJWTAuthentication]
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
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']

    @swagger_auto_schema(
        **swagger.update_operation(
            summary="Change password",
            description="Change the password of the currently authenticated user. Requires current password for verification.",
            serializer=ChangePasswordSerializer,
            
        )
    )
    def put(self, request, *args, **kwargs):
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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            protocol, domain = get_protocol_and_domain(request)
            subject = 'Password Reset Request'
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'uidb64': uidb64,
                'token': token,
                'protocol': protocol,
                'domain': domain,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        except CustomUser.DoesNotExist:
            pass  
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
    def post(self, request, *args, **kwargs):
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
    authentication_classes = [CookieJWTAuthentication]
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
            serializer=UserSerializer(many=True)
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
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

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
        operation_description="Verify user email using the token sent to their email address. Set is_home_owner=true to verify home_owner table instead of user table.",
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
            ),
            openapi.Parameter(
                'is_home_owner',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description='Set to True if verifying home_owner table instead of user table'
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
        is_home_owner = request.query_params.get('is_home_owner', 'false').lower() == 'true'
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            
            if is_home_owner:
                user = CustomHomeOwner.objects.get(pk=uid)
            else:
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
        except CustomHomeOwner.DoesNotExist:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "Invalid user"
            }, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(generics.CreateAPIView):
    """
    Verify user OTP sent to email or phone
    """
    serializer_class = OTPSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Verify OTP",
            description="Verify user OTP sent to email or phone. Requires email or phone_number and OTP. Set is_home_owner=true to verify home_owner table instead of user table.",
            serializer=OTPSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        otp = serializer.validated_data['otp']
        is_home_owner = serializer.validated_data.get('is_home_owner', False)
        
        # Test OTP for development/testing
        TEST_OTP = "555555"
        
        try:
            if is_home_owner:
                if email:
                    user = CustomHomeOwner.objects.get(email=email)
                else:
                    user = CustomHomeOwner.objects.get(phone_number=phone_number)
            else:
                if email:
                    user = CustomUser.objects.get(email=email)
                else:
                    user = CustomUser.objects.get(phone_number=phone_number)
        except (CustomUser.DoesNotExist, CustomHomeOwner.DoesNotExist):
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "Invalid user"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Skip OTP validation for test OTP
        if otp != TEST_OTP:
            if is_home_owner:
                otp_field = user.password_reset_otp
                otp_expires_field = user.password_reset_otp_expires
            else:
                otp_field = user.reset_password_token
                otp_expires_field = user.reset_password_token_expires
            
            if otp_field != otp:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "data": None,
                    "message": "Invalid OTP"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_expires_field and otp_expires_field < timezone.now():
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "data": None,
                    "message": "OTP has expired"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        user.email_verified = True
        
        if is_home_owner:
            user.is_verified = True
        
        # Clear OTP fields
        if is_home_owner:
            user.password_reset_otp = None
            user.password_reset_otp_expires = None
        else:
            user.reset_password_token = None
            user.reset_password_token_expires = None
        user.save()
        
        # Use appropriate serializer based on user type
        if is_home_owner:
            serializer = HomeOwnerSerializer(user)
        else:
            serializer = UserSerializer(user)
        
        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "data":None,
            "message": "OTP verified successfully"
        }, status=status.HTTP_200_OK)


class SendOTPView(generics.CreateAPIView):
    """
    Send OTP for verification (email or phone_number)
    """
    serializer_class = SendOTPSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        **swagger.create_operation(
            summary="Send OTP",
            description="Send OTP to user's email or phone for verification. Provide either email or phone_number (or both with verification_type). If only email is provided, verification_type defaults to 'email'. If only phone_number is provided, verification_type defaults to 'phone_number'. Set is_home_owner=true to look up home_owner table instead of user table.",
            serializer=SendOTPSerializer
        )
    )
    def post(self, request, *args, **kwargs):
        import random
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        verification_type = serializer.validated_data['verification_type']
        is_home_owner = serializer.validated_data.get('is_home_owner', False)
        is_forget_otp = serializer.validated_data.get('is_forget_otp', False)
        
       
        if not is_forget_otp:
           
            otp="555555"
            
            if verification_type == 'email':
                subject = 'Your OTP for Verification'
                message = f'Your OTP is: {otp}. This OTP will expire in 10 minutes.'
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                except Exception as e:
                    return Response({
                        "success": False,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "data": None,
                        "message": f"Failed to send OTP email: {str(e)}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": {
                        "email": email,
                        "verification_type": verification_type,
                        "otp": otp,
                        "message": f"OTP sent successfully to {verification_type}"
                    },
                    "message": "OTP sent successfully"
                }, status=status.HTTP_200_OK)
            
            elif verification_type == 'phone_number':
                return Response({
                    "success": True,
                    "statusCode": status.HTTP_200_OK,
                    "data": {
                        "phone_number": phone_number,
                        "verification_type": verification_type,
                        "otp": otp,
                        "message": "OTP sent to phone number"
                    },
                    "message": "OTP sent successfully"
                }, status=status.HTTP_200_OK)
        
        # If is_forget_otp is True, check the appropriate table
        user = None
        if is_home_owner:
            try:
                if verification_type == 'email':
                    user = CustomHomeOwner.objects.get(email=email)
                else:
                    user = CustomHomeOwner.objects.get(phone_number=phone_number)
            except CustomHomeOwner.DoesNotExist:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "data": None,
                    "message": "Home owner with this email or phone number does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                if verification_type == 'email':
                    user = CustomUser.objects.get(email=email)
                else:
                    user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_404_NOT_FOUND,
                    "data": None,
                    "message": "User with this email or phone number does not exist"
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate OTP and save to user
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        if is_home_owner:
            user.password_reset_otp = otp
            user.password_reset_otp_expires = timezone.now() + timezone.timedelta(minutes=10)
        else:
            user.reset_password_token = otp
            user.reset_password_token_expires = timezone.now() + timezone.timedelta(minutes=10)
        user.save()
        
        if verification_type == 'email':
            subject = 'Your OTP for Password Reset'
            message = f'Your OTP is: {otp}. This OTP will expire in 10 minutes.'
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception as e:
                return Response({
                    "success": False,
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "data": None,
                    "message": f"Failed to send OTP email: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "email": user.email,
                    "verification_type": verification_type,
                    "otp": otp,
                    "message": f"OTP sent successfully to {verification_type}"
                },
                "message": "OTP sent successfully"
            }, status=status.HTTP_200_OK)
        
        elif verification_type == 'phone_number':
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "phone_number": user.phone_number,
                    "verification_type": verification_type,
                    "otp": otp,
                    "message": "OTP sent to phone number"
                },
                "message": "OTP sent successfully"
            }, status=status.HTTP_200_OK)


class CustomTokenRefreshView(APIView):
    """
    Custom token refresh view that handles both CustomUser and CustomHomeOwner tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        refresh_token = request.data.get('refresh')
        is_home_owner = request.data.get('is_home_owner', False)
        
        if not refresh_token:
            return Response({
                "success": False,
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "data": None,
                "message": "Refresh token is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            
            # Get the user_id from the token
            user_id = token.payload.get('user_id')
            
            if user_id:
                # Check if user_id is a string (could be UUID or integer as string)
                if isinstance(user_id, str):
                    try:
                        # Try to convert to int for CustomUser
                        user_id_int = int(user_id)
                        user_id = user_id_int
                    except ValueError:
                        # It's a UUID, check if it's a valid user
                        if is_home_owner:
                            try:
                                user = CustomHomeOwner.objects.get(id=user_id)
                                # Update the token with the correct user_id
                                token.payload['user_id'] = str(user.id)
                            except CustomHomeOwner.DoesNotExist:
                                return Response({
                                    "success": False,
                                    "statusCode": status.HTTP_401_UNAUTHORIZED,
                                    "data": None,
                                    "message": "Invalid token - home owner not found"
                                }, status=status.HTTP_401_UNAUTHORIZED)
                        else:
                            try:
                                user = CustomUser.objects.get(id=user_id)
                                # Update the token with the correct user_id
                                token.payload['user_id'] = str(user.id)
                            except CustomUser.DoesNotExist:
                                return Response({
                                    "success": False,
                                    "statusCode": status.HTTP_401_UNAUTHORIZED,
                                    "data": None,
                                    "message": "Invalid token - user not found"
                                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate new access token
            access_token = str(token.access_token)
            
            return Response({
                "success": True,
                "statusCode": status.HTTP_200_OK,
                "data": {
                    "access": access_token
                },
                "message": "Token refreshed successfully"
            }, status=status.HTTP_200_OK)
            
        except (InvalidToken, TokenError) as e:
            return Response({
                "success": False,
                "statusCode": status.HTTP_401_UNAUTHORIZED,
                "data": None,
                "message": f"Invalid token: {str(e)}. Please login again."
            }, status=status.HTTP_401_UNAUTHORIZED)
