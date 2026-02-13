from rest_framework import serializers
from .models import Promotion
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from drf_yasg import openapi
import requests


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating promotions with file upload support"""
    
    user_limit = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    merchant_provider_img = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text='Merchant image URL (http://..., https://..., or base64 data URI)'
    )
    
    class Meta:
        model = Promotion
        fields = [
            "id",
            "code",
            "title",
            "description",
            "promo_type",
            "user_limit",
            "merchant_provider_name",
            "merchant_provider_img",
            "is_active",
            "start_date",
            "end_date",
            "created_at"
        ]
        read_only_fields = ["created_at", "code"]
        swagger_schema = {
            'required': ['title', 'description', 'promo_type', 'user_limit', 'merchant_provider_name', 'start_date', 'end_date'],
            'properties': {
                'title': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Title of the promotion'
                },
                'description': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Description of the promotion'
                },
                'promo_type': {
                    'type': openapi.TYPE_STRING,
                    'enum': ['Flat', 'Percentage'],
                    'description': 'Type of promotion'
                },
                'user_limit': {
                    'type': openapi.TYPE_NUMBER,
                    'description': 'Maximum number of users who can use this promotion'
                },
                'merchant_provider_name': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Name of the merchant or provider'
                },
                'merchant_provider_img': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Image URL - http://..., https://..., or base64 data URI'
                },
                'is_active': {
                    'type': openapi.TYPE_BOOLEAN,
                    'description': 'Whether the promotion is active (default: true)'
                },
                'start_date': {
                    'type': openapi.TYPE_STRING,
                    'format': 'date',
                    'description': 'Start date of the promotion (YYYY-MM-DD)'
                },
                'end_date': {
                    'type': openapi.TYPE_STRING,
                    'format': 'date',
                    'description': 'End date of the promotion (YYYY-MM-DD)'
                }
            }
        }
    
    def validate_merchant_provider_img(self, value):
        """Validate and process merchant image URL or base64"""
        if not value:
            return value
        
        if isinstance(value, str):
            if value.startswith('http://') or value.startswith('https://'):
                try:
                    response = requests.get(value)
                    if response.status_code == 200:
                        from django.core.files.base import ContentFile
                        import uuid
                        import os
                        filename = value.split('/')[-1].split('?')[0]
                        ext = filename.split('.')[-1] if '.' in filename and len(filename.split('.')[-1]) <= 5 else 'jpg'
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        return ContentFile(response.content, name=filename)
                except Exception as e:
                    raise serializers.ValidationError(f"Failed to download image from URL: {str(e)}")
            elif value.startswith('data:image'):
                import base64
                from django.core.files.base import ContentFile
                import uuid
                base64_data = value.split(',')[1] if ',' in value else value
                image_data = base64.b64decode(base64_data)
                ext = 'jpg'
                if 'png' in value:
                    ext = 'png'
                elif 'gif' in value:
                    ext = 'gif'
                elif 'webp' in value:
                    ext = 'webp'
                filename = f"{uuid.uuid4().hex}.{ext}"
                return ContentFile(image_data, name=filename)
        
        return value
    
    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError(_("Title is required"))
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("Promotion title must be at least 3 characters long"))
        return value
    
    def validate_user_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError(_("User limit must be greater than 0"))
        return value
    
    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        
        # Check if end_date is in the past
        if end_date and end_date < timezone.now().date():
            raise serializers.ValidationError({
                "end_date": _("End date cannot be in the past.")
            })
        
        # Check if end_date is greater than start_date
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": _("End date must be greater than start date.")
            })
        
        # Check for duplicate title
        title = data.get('title')
        if title:
            # For update, exclude current instance
            instance = getattr(self, 'instance', None)
            queryset = Promotion.objects.filter(title__iexact=title.strip())
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({
                    "title": _("A promotion with this title already exists. Please create a new one.")
                })
        
        return data
    
    def create(self, validated_data):
        """Create promotion with image handling"""
        merchant_provider_img = validated_data.pop('merchant_provider_img', None)
        promotion = Promotion.objects.create(**validated_data)
        
        if merchant_provider_img:
            promotion.merchant_provider_img = merchant_provider_img
            promotion.save(update_fields=['merchant_provider_img'])
        
        return promotion
    
    def update(self, instance, validated_data):
        """Update promotion with image handling"""
        merchant_provider_img = validated_data.pop('merchant_provider_img', None)
        
        if merchant_provider_img:
            instance.merchant_provider_img = merchant_provider_img
        
        return super().update(instance, validated_data)


class PromotionListSerializer(serializers.ModelSerializer):
    """Serializer for listing promotions with working image URLs"""
    
    merchant_name = serializers.CharField(source="merchant_provider_name", read_only=True)
    merchant_img_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = [
            "id",
            "code",
            "title",
            "description",
            "promo_type",
            "user_limit",
            "merchant_name",
            "merchant_img_url",
            "is_active",
            "start_date",
            "end_date",
            "created_at"
        ]
        swagger_schema = {
            'properties': {
                'id': {'type': openapi.TYPE_STRING, 'format': 'uuid'},
                'code': {'type': openapi.TYPE_STRING},
                'title': {'type': openapi.TYPE_STRING},
                'description': {'type': openapi.TYPE_STRING},
                'promo_type': {'type': openapi.TYPE_STRING},
                'user_limit': {'type': openapi.TYPE_NUMBER},
                'merchant_name': {'type': openapi.TYPE_STRING},
                'merchant_img_url': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Full working URL to the merchant image'
                },
                'is_active': {'type': openapi.TYPE_BOOLEAN},
                'start_date': {'type': openapi.TYPE_STRING, 'format': 'date'},
                'end_date': {'type': openapi.TYPE_STRING, 'format': 'date'},
                'created_at': {'type': openapi.TYPE_STRING, 'format': 'date-time'}
            }
        }
    
    def get_merchant_img_url(self, obj):
        """Get the full working URL for the merchant image"""
        if obj.merchant_provider_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.merchant_provider_img.url)
            from django.conf import settings
            return f"{settings.MEDIA_URL}{obj.merchant_provider_img}"
        return None


class PromotionDetailSerializer(serializers.ModelSerializer):
    """Serializer for promotion details with working image URLs"""
    
    user_limit = serializers.DecimalField(max_digits=10, decimal_places=2)
    merchant_img_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Promotion
        fields = "__all__"
        read_only_fields = ["created_at", "code"]
        swagger_schema = {
            'properties': {
                'merchant_img_url': {
                    'type': openapi.TYPE_STRING,
                    'description': 'Full working URL to the merchant image'
                }
            }
        }
    
    def get_merchant_img_url(self, obj):
        """Get the full working URL for the merchant image"""
        if obj.merchant_provider_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.merchant_provider_img.url)
            from django.conf import settings
            return f"{settings.MEDIA_URL}{obj.merchant_provider_img}"
        return None


class PromotionStatusSerializer(serializers.ModelSerializer):
    """Serializer for updating promotion status"""
    
    class Meta:
        model = Promotion
        fields = ["is_active"]
        swagger_schema = {
            'required': ['is_active'],
            'properties': {
                'is_active': {
                    'type': openapi.TYPE_BOOLEAN,
                    'description': 'Whether the promotion is active'
                }
            }
        }
    
    def validate_is_active(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError(_("is_active must be a boolean value"))
        return value


class PromotionDeleteSerializer(serializers.ModelSerializer):
    """Serializer for promotion deletion confirmation"""
    
    confirm = serializers.BooleanField()
    
    class Meta:
        model = Promotion
        fields = ["confirm"]
        swagger_schema = {
            'required': ['confirm'],
            'properties': {
                'confirm': {
                    'type': openapi.TYPE_BOOLEAN,
                    'description': 'Must be true to confirm deletion'
                }
            }
        }
    
    def validate_confirm(self, value):
        if value is not True:
            raise serializers.ValidationError(_("You must confirm deletion."))
        return value
