from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_email_verified)
        )

email_verification_token = EmailVerificationTokenGenerator()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if not self.user.email_verified:
            raise serializers.ValidationError({
                "detail": "Email is not verified. Please verify your email to proceed.",
                "code": "email_not_verified"
            })
        data['role'] = self.user.role
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['name'] = self.user.name
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['name'] = user.name
        token['email'] = user.email
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("name", 'email', 'password', "phone_number", "status", "role")

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data["name"],
            phone_number=validated_data['phone_number'],
            role=validated_data['role'],
            status=validated_data.get("status", True)
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=15)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.tokens import RefreshToken
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if not email and not phone_number:
            raise serializers.ValidationError({"detail": "Either email or phone_number is required"})
        
        if not password:
            raise serializers.ValidationError({"detail": "Password is required"})
        
        if email:
            user = authenticate(request=None, username=email, password=password)
        else:
            try:
                from .models import CustomUser
                user_obj = CustomUser.objects.get(phone_number=phone_number)
                user = authenticate(request=None, username=user_obj.email, password=password)
            except CustomUser.DoesNotExist:
                user = None
        
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials"})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled"})
        
        refresh = RefreshToken.for_user(user)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        
        attrs['user'] = user
        attrs['tokens'] = tokens
        attrs['role'] = getattr(user, 'role', None)
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'phone_number', 'status', 'role', 'email_verified')
        read_only_fields = ('id', 'email_verified')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'phone_number', 'status', 'role', 'email_verified')
        read_only_fields = ('id', 'email', 'role', 'email_verified')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as old password"})
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=15)
    verification_type = serializers.ChoiceField(
        choices=['email', 'phone_number'],
        required=False,
        help_text="Type of verification: 'email' or 'phone_number'. Optional - will be inferred from provided field."
    )
    is_home_owner = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Set to True if checking home_owner table instead of user table"
    )
    is_forget_otp = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Set to True to check from database tables (for forget password). False to use cache (for pre-registration)."
    )

    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        verification_type = attrs.get('verification_type')
        
        if not email and not phone_number:
            raise serializers.ValidationError({"non_field_errors": ["Either email or phone_number is required"]})
        
        if email and phone_number and not verification_type:
            raise serializers.ValidationError({"verification_type": "verification_type is required when both email and phone_number are provided"})
    
        if email and not phone_number:
            attrs['verification_type'] = 'email'
        
        if phone_number and not email:
            attrs['verification_type'] = 'phone_number'
        
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=8)
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=15)
    otp = serializers.CharField(required=True, max_length=6)
    is_home_owner = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Set to True if verifying home_owner table instead of user table"
    )
    is_forget_otp = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Set to True to verify from database tables (for forget password). False to verify from cache (for pre-registration)."
    )

    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        
        if not email and not phone_number:
            raise serializers.ValidationError({"detail": "Either email or phone_number is required"})
        
        return attrs
