from rest_framework import serializers
from .models import Promotion
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class PromotionSerializer(serializers.ModelSerializer):
    user_limit = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    
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
            "is_active",
            "start_date",
            "end_date",
            "created_at"
        ]
        read_only_fields = ["created_at", "code"]

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
        
        return data


class PromotionListSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(source="merchant_provider_name", read_only=True)
    
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
            "is_active",
            "start_date",
            "end_date",
            "created_at"
        ]


class PromotionDetailSerializer(serializers.ModelSerializer):
    user_limit = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        model = Promotion
        fields = "__all__"
        read_only_fields = ["created_at", "code"]


class PromotionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ["is_active"]
    
    def validate_is_active(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError(_("is_active must be a boolean value"))
        return value


class PromotionDeleteSerializer(serializers.ModelSerializer):
    confirm = serializers.BooleanField()

    class Meta:
        model = Promotion
        fields = ["confirm"]
    
    def validate_confirm(self, value):
        if value is not True:
            raise serializers.ValidationError(_("You must confirm deletion."))
        return value
