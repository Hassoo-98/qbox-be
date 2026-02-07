from rest_framework import serializers
from .models import Qbox, QboxAccessQRCode, QboxAccessUser
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings

class QboxSerializer(serializers.ModelSerializer):
    packages = serializers.SerializerMethodField()
    
    class Meta:
        model = Qbox
        fields = [
            "id", "qbox_id", "homeowner", "homeowner_name_snapshot",
            "short_address_snapshot", "city_snapshot", "status",
            "led_indicator", "camera_status", "last_online",
            "activation_date", "qbox_image", "created_at", "updated_at",
            "packages"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_packages(self, obj):
        from packages.serializers import PackageSerializer
        return PackageSerializer(obj.packages.all(), many=True).data

class QboxListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qbox
        fields = [
            "id", "qbox_id", "homeowner_name_snapshot",
            "short_address_snapshot", "city_snapshot", "status",
            "led_indicator", "camera_status", "last_online",
            "activation_date", "qbox_image"
        ]

class QboxCreateSerializer(serializers.ModelSerializer):
    homeowner = serializers.CharField(required=False, allow_null=True, help_text="Homeowner UUID (optional - will be assigned when homeowner creates account with qbox_id)")

    class Meta:
        model = Qbox
        fields = [
            "qbox_id", "homeowner", "status",
            "led_indicator", "camera_status", "qbox_image"
        ]

    def create(self, validated_data):
        homeowner_uuid = validated_data.pop('homeowner', None)
        from home_owner.models import CustomHomeOwner
        
        homeowner_obj = None
        if homeowner_uuid:
            try:
                homeowner_obj = CustomHomeOwner.objects.get(id=homeowner_uuid)
            except CustomHomeOwner.DoesNotExist:
                pass
        
        qbox = Qbox.objects.create(homeowner=homeowner_obj, **validated_data)
        if qbox.homeowner:
            qbox.sync_with_homeowner(save=True)
        return qbox

class QboxUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qbox
        fields = [
            "homeowner", "status",
            "led_indicator", "camera_status", "qbox_image"
        ]

    def update(self, instance, validated_data):
        old_homeowner = instance.homeowner
        instance = super().update(instance, validated_data)
        # Sync with homeowner if assigned or changed
        if instance.homeowner:
            instance.sync_with_homeowner(save=True)
        elif old_homeowner and not instance.homeowner:
            # Clear snapshots if homeowner is removed
            instance.homeowner_name_snapshot = ""
            instance.short_address_snapshot = ""
            instance.city_snapshot = ""
            instance.save(update_fields=['homeowner_name_snapshot', 'short_address_snapshot', 'city_snapshot'])
        return instance

class QboxStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Qbox.Status.choices, required=True)
    is_active = serializers.BooleanField(required=True)


class VerifyQboxIdSerializer(serializers.Serializer):
    qbox_id = serializers.CharField(required=False, max_length=20, help_text="Unique device identifier of the QBox")
    
    def validate(self, attrs):
        qbox_id = attrs.get('qbox_id') or attrs.get('qbox-id')
        
        if not qbox_id:
            raise serializers.ValidationError({"detail": "qbox_id is required"})
        
        attrs['qbox_id'] = qbox_id
        return attrs


# QR Code Serializers

class QboxAccessQRCodeCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new access QR code
    """
    qbox_id = serializers.CharField(required=True, help_text="Qbox ID to generate QR code for")
    name = serializers.CharField(required=True, max_length=100, help_text="Name for this QR code (e.g., 'Morning shift entrance')")
    location = serializers.CharField(required=False, max_length=200, default="", help_text="Location description (e.g., 'Box Main Entrance')")
    address = serializers.CharField(required=False, max_length=500, default="", help_text="Full address")
    max_users = serializers.IntegerField(required=True, default=5, min_value=1, help_text="Maximum number of users who can use this QR code")
    duration_type = serializers.ChoiceField(
        required=True,
        choices=QboxAccessQRCode.DurationType.choices,
        default=QboxAccessQRCode.DurationType.DAYS,
        help_text="Duration type: 'days' or 'minutes'"
    )
    valid_duration = serializers.IntegerField(required=True, default=1, min_value=1, help_text="Duration value based on duration_type")

    def validate(self, attrs):
        qbox_id = attrs.get('qbox_id')
        try:
            qbox = Qbox.objects.get(qbox_id=qbox_id)
            attrs['qbox'] = qbox
        except Qbox.DoesNotExist:
            raise serializers.ValidationError({"qbox_id": f"Qbox with ID '{qbox_id}' not found"})
        return attrs

    def create(self, validated_data):
        import secrets
        from io import BytesIO
        from django.core.files import File
        
        qbox = validated_data.pop('qbox')
        qbox_id = validated_data.pop('qbox_id')  # Remove qbox_id as it's not a model field
        
        # Homeowner is optional - only set if explicitly provided
        homeowner = None
        
        # Generate unique access token
        access_token = secrets.token_urlsafe(32)
        
        qr_code = QboxAccessQRCode.objects.create(
            qbox=qbox,
            homeowner=homeowner,
            access_token=access_token,
            **validated_data
        )
        
        # Generate and save QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # QR code data contains comprehensive information for display
        qr_data = {
            "qbox_id": qbox.qbox_id,
            "qr_name": qr_code.name,
            "location": qr_code.location,
            "short_address": qbox.short_address_snapshot,
            "city": qbox.city_snapshot,
            "max_users": qr_code.max_users,
            "valid_duration": f"{qr_code.valid_duration} {qr_code.duration_type}",
            "qbox_image": qbox.qbox_image if qbox.qbox_image else None,
            "expires_at": qr_code.expires_at.isoformat() if qr_code.expires_at else None
        }
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save QR code image to model
        filename = f"qrcode_{qr_code.id}.png"
        qr_code.qr_code_image.save(filename, File(buffer), save=True)
        qr_code.qr_code_url = qr_code.qr_code_image.url
        qr_code.save(update_fields=['qr_code_url'])
        
        return qr_code


class QboxAccessQRCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for QR code response
    """
    remaining_users = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    expiresIn = serializers.SerializerMethodField()
    qbox_id = serializers.CharField(source='qbox.qbox_id', read_only=True)
    qr_code_image = serializers.SerializerMethodField()
    
    class Meta:
        model = QboxAccessQRCode
        fields = [
            "id", "qbox", "qbox_id", "homeowner",
            "name", "location", "address",
            "max_users", "current_users", "remaining_users",
            "duration_type", "valid_duration", "expires_at",
            "access_token", "qr_code_image",
            "is_active", "status", "expiresIn",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "access_token"]
    
    def get_remaining_users(self, obj):
        return obj.max_users - obj.current_users
    
    def get_status(self, obj):
        return obj.get_status()
    
    def get_expiresIn(self, obj):
        return obj.get_expires_in()
    
    def get_qr_code_image(self, obj):
        """Generate and return full QR code image URL"""
        from django.conf import settings
        
        if obj.qr_code_url:
            return obj.qr_code_url
        
        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # QR code data contains comprehensive information for display
        qr_data = {
            "qbox_id": obj.qbox.qbox_id,
            "qr_name": obj.name,
            "location": obj.location,
            "short_address": obj.qbox.short_address_snapshot,
            "city": obj.qbox.city_snapshot,
            "max_users": obj.max_users,
            "valid_duration": f"{obj.valid_duration} {obj.duration_type}",
            "qbox_image": obj.qbox.qbox_image if obj.qbox.qbox_image else None,
            "expires_at": obj.expires_at.isoformat() if obj.expires_at else None
        }
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Save to model
        filename = f"qrcode_{obj.id}.png"
        obj.qr_code_image.save(filename, File(buffer), save=True)
        obj.qr_code_url = obj.qr_code_image.url
        obj.save(update_fields=['qr_code_url', 'qr_code_image'])
        
        return obj.qr_code_url


class QboxAccessQRCodeListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing QR codes
    """
    remaining_users = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    qbox_id = serializers.CharField(source='qbox.qbox_id', read_only=True)
    
    class Meta:
        model = QboxAccessQRCode
        fields = [
            "id", "qbox", "qbox_id",
            "name", "location", "address",
            "max_users", "current_users", "remaining_users",
            "duration_type", "valid_duration", "expires_at",
            "is_active", "is_valid",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]
    
    def get_remaining_users(self, obj):
        return obj.max_users - obj.current_users
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class QboxAccessQRCodeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QboxAccessQRCode
        fields = [
            "name", "location", "address",
            "max_users", "duration_type", "valid_duration",
            "is_active"
        ]


class QboxAccessUserSerializer(serializers.ModelSerializer):
    qr_code_name = serializers.CharField(source='qr_code.name', read_only=True)
    qbox_id = serializers.CharField(source='qr_code.qbox.qbox_id', read_only=True)
    
    class Meta:
        model = QboxAccessUser
        fields = [
            "id", "qr_code", "qr_code_name", "qbox_id",
            "user_identifier", "user_name",
            "accessed_at", "access_type"
        ]
        read_only_fields = ["id", "accessed_at"]


class QboxAccessQRCodeHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for QR Code History Log
    """
    validforUsers = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    expiresIn = serializers.SerializerMethodField()
    qbox_id = serializers.CharField(source='qbox.qbox_id', read_only=True)
    
    class Meta:
        model = QboxAccessQRCode
        fields = [
            "id", "qbox_id", "name", "status",
            "validforUsers", "expiresIn",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]
    
    def get_validforUsers(self, obj):
        return obj.max_users - obj.current_users
    
    def get_status(self, obj):
        return obj.get_status()
    
    def get_expiresIn(self, obj):
        return obj.get_expires_in()


class QboxAccessQRCodeStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating QR code status (Active/Inactive)"""
    status = serializers.ChoiceField(
        choices=["Active", "Inactive"],
        required=True,
        help_text="New status: Active or Inactive"
    )


class QboxAccessRequestSerializer(serializers.Serializer):
    """
    Serializer for validating access requests via QR code
    """
    access_token = serializers.CharField(required=True, help_text="Access token from the QR code")
    user_identifier = serializers.CharField(required=True, help_text="User identifier (email, phone, or custom ID)")
    user_name = serializers.CharField(required=False, allow_blank=True, default="", help_text="User's name if provided")

    def validate_access_token(self, value):
        try:
            qr_code = QboxAccessQRCode.objects.get(access_token=value)
            if not qr_code.is_valid():
                raise serializers.ValidationError("This QR code has expired or reached maximum users")
            return value
        except QboxAccessQRCode.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code")
