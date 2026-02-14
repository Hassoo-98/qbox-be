from rest_framework import serializers
from django.core.files.base import ContentFile
import requests
import base64
import uuid
from .models import CustomHomeOwner, CustomHomeOwnerAddress
from q_box.models import Qbox
class HomeOwnerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomHomeOwnerAddress
        fields = [
            'short_address', 'city', 'district', 'street',
            'postal_code', 'building_number', 'secondary_building_number'
        ]

class InstallationSerializer(serializers.Serializer):
    location_preference = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Preferred location for QBox installation (e.g. mainDoor, balcony)"
    )
    access_instruction = serializers.CharField(
        required=True,
        max_length=500,
        help_text="Instructions how to access the installation location"
    )
    qbox_image_url = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="QBox image URL - http://..., https://..., or base64 data URI"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Installation details for QBox"
    )


class HomeOwnerSerializer(serializers.ModelSerializer):
    address = HomeOwnerAddressSerializer(read_only=True)
    qboxes = serializers.SerializerMethodField()
    installation_qbox_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomHomeOwner
        fields = [
            "id", "full_name", "email", "phone_number", "secondary_phone_number",
            "is_verified", "email_verified", "phone_verified", "address",
            "installation_location_preference", "installation_access_instruction",
            "installation_qbox_image_url",
            "is_active", "date_joined", "qboxes"
        ]
        read_only_fields = ["id", "date_joined", "is_verified", "email_verified", "phone_verified"]

    def get_qboxes(self, obj):
        from q_box.serializers import QboxListSerializer
        return QboxListSerializer(obj.qboxes.all(), many=True, context=self.context).data

    def get_installation_qbox_image_url(self, obj):
        if not obj.installation_qbox_image_url:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.installation_qbox_image_url.url)
        return obj.installation_qbox_image_url.url


class HomeOwnerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=1)
    address = HomeOwnerAddressSerializer(required=True)
    qbox_id = serializers.CharField(required=True, max_length=20)
    
    installation = InstallationSerializer(required=True)  
    
    installation_image_base64 = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Base64 encoded image (data:image/jpeg;base64,...) - only for small images!"
    )

    class Meta:
        model = CustomHomeOwner
        fields = [
            'full_name', 'email', 'phone_number', 'secondary_phone_number',
            'password', 'qbox_id', 'address', 'installation',
            'installation_image_base64'
        ]

    def validate_installation_image_base64(self, value):
        if not value:
            return None
            
        if not value.startswith('data:image'):
            raise serializers.ValidationError("Must be a data URI (data:image/...;base64,...)")
            
        try:
            header, encoded = value.split(',', 1)
            image_data = base64.b64decode(encoded)
            
            # Very basic size limit (example: ~4MB after decode)
            if len(image_data) > 4 * 1024 * 1024:
                raise serializers.ValidationError("Image too large (>4MB after decoding)")
                
            content_type = header.split(';')[0].split(':')[1]
            ext = 'jpg'
            if 'png' in content_type:
                ext = 'png'
            elif 'webp' in content_type:
                ext = 'webp'
                
            filename = f"install-{uuid.uuid4().hex}.{ext}"
            return ContentFile(image_data, name=filename)
            
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 image: {str(e)}")

    def create(self, validated_data):
        installation_data = validated_data.pop('installation')
        address_data = validated_data.pop('address')
        image_content_file = validated_data.pop('installation_image_base64', None)
        qbox_id = validated_data.pop('qbox_id')
        
        # Extract installation fields
        installation_location_preference = installation_data.get('location_preference')
        installation_access_instruction = installation_data.get('access_instruction')
        installation_description = installation_data.get('description', '')
        installation_qbox_image_url = installation_data.get('qbox_image_url', '')
        
        address = CustomHomeOwnerAddress.objects.create(**address_data)
        homeowner = CustomHomeOwner.objects.create_user(
            email=validated_data.pop('email'),
            full_name=validated_data.pop('full_name'),
            phone_number=validated_data.pop('phone_number', ''),
            password=validated_data.pop('password'),
            address=address,
            installation_location_preference=installation_location_preference,
            installation_access_instruction=installation_access_instruction,
            **validated_data
        )

        # Handle image: prefer base64, fallback to qbox_image_url
        if image_content_file:
            homeowner.installation_qbox_image_url = image_content_file
            homeowner.save(update_fields=['installation_qbox_image_url'])
        elif installation_qbox_image_url:
            # If it's a URL, store it directly
            if installation_qbox_image_url.startswith('http'):
                homeowner.installation_qbox_image_url = installation_qbox_image_url
            elif installation_qbox_image_url.startswith('data:image'):
                # Handle base64 data URI from qbox_image_url field
                try:
                    import base64
                    import uuid
                    header, encoded = installation_qbox_image_url.split(',', 1)
                    image_data = base64.b64decode(encoded)
                    content_type = header.split(';')[0].split(':')[1]
                    ext = 'jpg'
                    if 'png' in content_type:
                        ext = 'png'
                    elif 'webp' in content_type:
                        ext = 'webp'
                    filename = f"install-{uuid.uuid4().hex}.{ext}"
                    homeowner.installation_qbox_image_url = ContentFile(image_data, name=filename)
                except Exception:
                    pass
            homeowner.save(update_fields=['installation_qbox_image_url'])

        try:
            qbox = Qbox.objects.get(qbox_id=qbox_id)
            qbox.homeowner = homeowner
            if homeowner.installation_qbox_image_url:
                request = self.context.get('request')
                qbox.qbox_image = request.build_absolute_uri(
                    homeowner.installation_qbox_image_url.url
                ) if request else homeowner.installation_qbox_image_url.url
            qbox.sync_with_homeowner(save=True)
            qbox.save()
        except Qbox.DoesNotExist:
            pass

        return homeowner
class HomeOwnerUpdateSerializer(serializers.ModelSerializer):
    address = HomeOwnerAddressSerializer(required=False)
    qbox_image = serializers.FileField(required=False, allow_null=True)
    installation_qbox_image_url = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Only if already uploaded elsewhere"
    )

    class Meta:
        model = CustomHomeOwner
        fields = [
            "full_name", "phone_number", "secondary_phone_number",
            "address", "installation_location_preference",
            "installation_access_instruction",
            "installation_qbox_image_url", "qbox_image"
        ]

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        qbox_image = validated_data.pop('qbox_image', None)
        image_url = validated_data.pop('installation_qbox_image_url', None)

        if address_data:
            if instance.address:
                for k, v in address_data.items():
                    setattr(instance.address, k, v)
                instance.address.save()
            else:
                address = CustomHomeOwnerAddress.objects.create(**address_data)
                instance.address = address

        if qbox_image:
            instance.installation_qbox_image_url = qbox_image
        elif image_url:
            instance.installation_qbox_image_url = image_url

        return super().update(instance, validated_data)


class HomeOwnerStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomHomeOwner
        fields = [
            "is_active",
            "is_verified",
            "email_verified",
            "phone_verified"
        ]


class HomeOwnerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class HomeOwnerResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)