
from rest_framework import serializers
from .models import CustomHomeOwner, CustomHomeOwnerAddress
import requests


class HomeOwnerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomHomeOwnerAddress
        fields = [
            'short_address', 'city', 'district', 'street',
            'postal_code', 'building_number', 'secondary_building_number'
        ]


class InstallationSerializer(serializers.Serializer):
    """Serializer for installation details during home owner creation"""
    location_preference = serializers.CharField(required=True, max_length=255, help_text="Preferred location for QBox installation")
    access_instruction = serializers.CharField(required=True, max_length=500, help_text="Instructions for accessing the installation location")
    qbox_image_url = serializers.CharField(required=False, allow_blank=True, help_text='QBox image URL - http://..., https://..., or base64 data URI')


class HomeOwnerSerializer(serializers.ModelSerializer):
    address = HomeOwnerAddressSerializer(read_only=True)
    qboxes = serializers.SerializerMethodField()
    installation_qbox_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomHomeOwner
        fields = [
            "id", "full_name", "email", "phone_number", "secondary_phone_number",
            "is_verified", "email_verified", "phone_verified", "address",
            "installation_location_preference", "installation_access_instruction", "installation_qbox_image_url",
            "is_active", "date_joined", "qboxes"
        ]
        read_only_fields = ["id", "date_joined", "is_verified", "email_verified", "phone_verified"]

    def get_qboxes(self, obj):
        from q_box.serializers import QboxListSerializer
        return QboxListSerializer(obj.qboxes.all(), many=True).data
    
    def get_installation_qbox_image_url(self, obj):
        """Return full working URL for the installation image"""
        from django.conf import settings
        if obj.installation_qbox_image_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.installation_qbox_image_url.url)
            return f"{settings.MEDIA_URL}{obj.installation_qbox_image_url}"
        return None


class HomeOwnerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    address = HomeOwnerAddressSerializer(required=False)
    qbox_id = serializers.CharField(required=True, max_length=20, help_text="QBox device ID to assign to this home owner")
    installation = InstallationSerializer(required=True, help_text="Installation details for QBox")

    class Meta:
        model = CustomHomeOwner
        fields = [
            "full_name", "email", "phone_number", "secondary_phone_number",
            "password", "address", "installation", "qbox_id"
        ]
    
    def validate_installation(self, value):
        """Validate and process installation image URL"""
        qbox_image_url = value.get('qbox_image_url')
        if qbox_image_url:
            value['qbox_image_url'] = self._process_image_url(qbox_image_url)
        return value
    
    def _process_image_url(self, url_value):
        """Process image URL or base64 and return saved file"""
        if not url_value:
            return None
        
        if isinstance(url_value, str):
            if url_value.startswith('http://') or url_value.startswith('https://'):
                try:
                    response = requests.get(url_value)
                    if response.status_code == 200:
                        from django.core.files.base import ContentFile
                        import uuid
                        import os
                        filename = url_value.split('/')[-1].split('?')[0]
                        ext = filename.split('.')[-1] if '.' in filename and len(filename.split('.')[-1]) <= 5 else 'jpg'
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        return ContentFile(response.content, name=filename)
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to download image from URL: {str(e)}")
            elif url_value.startswith('data:image'):
                import base64
                from django.core.files.base import ContentFile
                import uuid
                base64_data = url_value.split(',')[1] if ',' in url_value else url_value
                image_data = base64.b64decode(base64_data)
                ext = 'jpg'
                if 'png' in url_value:
                    ext = 'png'
                elif 'gif' in url_value:
                    ext = 'gif'
                elif 'webp' in url_value:
                    ext = 'webp'
                filename = f"{uuid.uuid4().hex}.{ext}"
                return ContentFile(image_data, name=filename)
        
        return url_value
    
    def create(self, validated_data):
        from q_box.models import Qbox
        
        qbox_id = validated_data.pop('qbox_id', None)
        address_data = validated_data.pop('address', None)
        installation_data = validated_data.pop('installation', None)
        
        # Extract installation fields
        installation_location_preference = None
        installation_access_instruction = None
        installation_qbox_image = None
        
        if installation_data:
            installation_location_preference = installation_data.get('location_preference')
            installation_access_instruction = installation_data.get('access_instruction')
            installation_qbox_image = installation_data.get('qbox_image_url')
        
        user = CustomHomeOwner.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password'],
            installation_location_preference=installation_location_preference,
            installation_access_instruction=installation_access_instruction,
            **{k: v for k, v in validated_data.items() if k not in [
                'email', 'full_name', 'phone_number', 'password', 
                'installation_location_preference', 'installation_access_instruction', 
                'installation_qbox_image_url', 'qbox_id', 'address', 'installation'
            ]}
        )
        
        # Save the image file if provided
        if installation_qbox_image:
            user.installation_qbox_image_url = installation_qbox_image
            user.save(update_fields=['installation_qbox_image_url'])
        
        if address_data:
            address = CustomHomeOwnerAddress.objects.create(**address_data)
            user.address = address
            user.save()
        
        if qbox_id:
            try:
                qbox = Qbox.objects.get(qbox_id=qbox_id)
                if not qbox.homeowner:
                    qbox.homeowner = user
                    if user.installation_qbox_image_url:
                        qbox.qbox_image = user.installation_qbox_image_url.url
                    qbox.sync_with_homeowner(save=True)
                    qbox.save()
            except Qbox.DoesNotExist:
                pass
        
        return user


class HomeOwnerUpdateSerializer(serializers.ModelSerializer):
    address = HomeOwnerAddressSerializer(required=False)
    installation_qbox_image_url = serializers.CharField(required=False, allow_blank=True, help_text="QBox image URL (http://..., https://..., or base64 data URI)")

    class Meta:
        model = CustomHomeOwner
        fields = [
            "full_name", "phone_number", "secondary_phone_number",
            "preferred_installment_location", "installation_qbox_image_url", "address"
        ]
    
    def validate_installation_qbox_image_url(self, value):
        """Validate and process installation image URL"""
        if value:
            return self._process_image_url(value)
        return value
    
    def _process_image_url(self, url_value):
        """Process image URL or base64 and return saved file"""
        if not url_value:
            return None
        
        if isinstance(url_value, str):
            if url_value.startswith('http://') or url_value.startswith('https://'):
                try:
                    response = requests.get(url_value)
                    if response.status_code == 200:
                        from django.core.files.base import ContentFile
                        import uuid
                        import os
                        filename = url_value.split('/')[-1].split('?')[0]
                        ext = filename.split('.')[-1] if '.' in filename and len(filename.split('.')[-1]) <= 5 else 'jpg'
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        return ContentFile(response.content, name=filename)
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to download image from URL: {str(e)}")
            elif url_value.startswith('data:image'):
                import base64
                from django.core.files.base import ContentFile
                import uuid
                base64_data = url_value.split(',')[1] if ',' in url_value else url_value
                image_data = base64.b64decode(base64_data)
                ext = 'jpg'
                if 'png' in url_value:
                    ext = 'png'
                elif 'gif' in url_value:
                    ext = 'gif'
                elif 'webp' in url_value:
                    ext = 'webp'
                filename = f"{uuid.uuid4().hex}.{ext}"
                return ContentFile(image_data, name=filename)
        
        return url_value
    
    def update(self, instance, validated_data):
        installation_qbox_image_url = validated_data.pop('installation_qbox_image_url', None)
        
        if installation_qbox_image_url:
            instance.installation_qbox_image_url = installation_qbox_image_url
        
        return super().update(instance, validated_data)


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


class HomeOwnerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=15)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        from rest_framework_simplejwt.tokens import RefreshToken
        
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if not email and not phone_number:
            raise serializers.ValidationError({"detail": "Either email or phone_number is required"})
        
        if not password:
            raise serializers.ValidationError({"detail": "Password is required"})
        
        user = None
        if email:
            try:
                user = CustomHomeOwner.objects.get(email=email)
            except CustomHomeOwner.DoesNotExist:
                user = None
        else:
            try:
                user = CustomHomeOwner.objects.get(phone_number=phone_number)
            except CustomHomeOwner.DoesNotExist:
                user = None
        
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials"})
        
        # Check password directly instead of using authenticate()
        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Invalid credentials"})
        
        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled"})
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        
        attrs['user'] = user
        attrs['tokens'] = tokens
        return attrs


class HomeOwnerResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        try:
            user = CustomHomeOwner.objects.get(email=email)
        except CustomHomeOwner.DoesNotExist:
            raise serializers.ValidationError({"detail": "User with this email does not exist"})
        
        attrs['user'] = user
        return attrs
