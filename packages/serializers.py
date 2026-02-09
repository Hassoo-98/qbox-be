from rest_framework import serializers
from .models import Package, PackageDetails
import uuid

class PackageDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageDetails
        fields = ["id", "package_type", "package_size", "package_weight", "summary"]

class PackageSerializer(serializers.ModelSerializer):
    details = PackageDetailsSerializer(read_only=True)
    
    class Meta:
        model = Package
        fields = [
            "id", "qbox", "tracking_id", "merchant_name",
            "service_provider", "driver_name", "qr_code",
            "package_status", "shipment_status", "last_update",
            "created_at", "details"
        ]
        read_only_fields = ["id", "created_at", "last_update"]

class PackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            "id", "tracking_id", "merchant_name",
            "service_provider", "driver_name",
            "package_status", "shipment_status", "created_at"
        ]

class PackageCreateSerializer(serializers.ModelSerializer):
    details = PackageDetailsSerializer(required=False)
    
    class Meta:
        model = Package
        fields = [
            "qbox", "tracking_id", "merchant_name",
            "service_provider", "driver_name", "qr_code",
            "package_status", "shipment_status", "details"
        ]
        extra_kwargs = {
            "tracking_id": {"required": False, "allow_blank": True}
        }

    def create(self, validated_data):
        # Auto-generate tracking_id if not provided
        if not validated_data.get('tracking_id'):
            validated_data['tracking_id'] = f"TRK-{str(uuid.uuid4())[:8].upper()}"
        
        details_data = validated_data.pop('details', None)
        package = Package.objects.create(**validated_data)
        
        if details_data:
            details = PackageDetails.objects.create(**details_data)
            package.details = details
            package.save()
        
        return package

class PackageUpdateSerializer(serializers.ModelSerializer):
    details = PackageDetailsSerializer(required=False)
    
    class Meta:
        model = Package
        fields = [
            "qbox", "merchant_name",
            "service_provider", "driver_name", "qr_code",
            "package_status", "shipment_status", "details"
        ]

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        
        if details_data:
            if instance.details:
                for key, value in details_data.items():
                    setattr(instance.details, key, value)
                instance.details.save()
            else:
                details = PackageDetails.objects.create(**details_data)
                instance.details = details
                instance.save()
        
        return instance


class PackageStatusUpdateSerializer(serializers.Serializer):
    package_status = serializers.ChoiceField(choices=Package.PackageStatus.choices, required=True)
    is_active = serializers.BooleanField(required=True)
