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
        
        # Add user data to response
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
