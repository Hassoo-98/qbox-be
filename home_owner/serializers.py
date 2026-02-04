
from rest_framework import serializers
from .models import CustomHomeOwner, CustomHomeOwnerAddress

class HomeOwnerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomHomeOwnerAddress
        fields = [
            'short_address', 'city', 'district', 'street',
            'postal_code', 'building_number', 'secondary_building_number'
        ]


class HomeOwnerSerializer(serializers.ModelSerializer):
    address = HomeOwnerAddressSerializer(read_only=True)
    qboxes = serializers.SerializerMethodField()

    class Meta:
        model = CustomHomeOwner
        fields = [
            "id", "full_name", "email", "phone_number", "secondary_phone_number",
            "is_verified", "email_verified", "phone_verified", "address", "preferred_installment_location",
            "is_active", "date_joined", "qboxes"
        ]
        read_only_fields = ["id", "date_joined", "is_verified", "email_verified", "phone_verified"]

    def get_qboxes(self, obj):
        from q_box.serializers import QboxListSerializer
        return QboxListSerializer(obj.qboxes.all(), many=True).data


class HomeOwnerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    address = HomeOwnerAddressSerializer(required=False)

    class Meta:
        model = CustomHomeOwner
        fields = [
            "full_name", "email", "phone_number", "secondary_phone_number",
            "password", "address", "preferred_installment_location"
        ]

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        
        user = CustomHomeOwner.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            **{k: v for k, v in validated_data.items() if k not in ['email', 'full_name', 'phone_number', 'password']}
        )

        if address_data:
            address = CustomHomeOwnerAddress.objects.create(**address_data)
            user.address = address
            user.save()

        return user


class HomeOwnerUpdateSerializer(serializers.ModelSerializer):
    address = HomeOwnerAddressSerializer(required=False)

    class Meta:
        model = CustomHomeOwner
        fields = [
            "full_name", "phone_number", "secondary_phone_number",
            "preferred_installment_location", "qbox_image", "address"
        ]


class HomeOwnerStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomHomeOwner
        fields = ["is_active", "is_verified", "email_verified", "phone_verified"]
        extra_kwargs = {
            "is_active": {"required": False},
            "is_verified": {"required": False},
            "email_verified": {"required": False},
            "phone_verified": {"required": False},
        }


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class VerifyPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10, required=True)


class VerifyQBoxSerializer(serializers.Serializer):
    qbox_id = serializers.CharField(max_length=20, required=True)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    verification_type = serializers.ChoiceField(
        choices=['email', 'phone'],
        required=True
    )


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    send_via = serializers.ChoiceField(
        choices=['email', 'phone'],
        default='email'
    )


class VerifyForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    send_via = serializers.ChoiceField(
        choices=['email', 'phone'],
        default='email'
    )


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)