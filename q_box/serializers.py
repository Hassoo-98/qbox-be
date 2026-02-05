from rest_framework import serializers
from .models import Qbox

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
        # Handle homeowner field - convert UUID string to object if provided
        homeowner_uuid = validated_data.pop('homeowner', None)
        from home_owner.models import CustomHomeOwner
        
        homeowner_obj = None
        if homeowner_uuid:
            try:
                homeowner_obj = CustomHomeOwner.objects.get(id=homeowner_uuid)
            except CustomHomeOwner.DoesNotExist:
                pass
        
        qbox = Qbox.objects.create(homeowner=homeowner_obj, **validated_data)
        # Sync with homeowner if assigned
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
    qbox_id = serializers.CharField(required=True, max_length=20, help_text="Unique device identifier of the QBox")
