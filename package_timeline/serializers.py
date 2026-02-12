from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import PackageTimeline
from packages.models import Package

class PackageTimelineSerializer(serializers.ModelSerializer):
    package_status = serializers.CharField(source='package.shipment_status', read_only=True)
    package_city = serializers.CharField(source='package.city', read_only=True)
    issue_related_to = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model=PackageTimeline
        fields=(
            "id",
            "date_and_time",
            "status",
            "description",
            "package",
            "package_status",
            "package_city",
            "issue_related_to"
        )
        read_only_fields=["date_and_time", "package_status", "package_city"]
        extra_kwargs = {
            'city': {'write_only': True}  # Explicitly reject city field
        }
    
    def validate(self, data):
        """
        Auto-populate status from package if not provided
        """
        # Check for forbidden fields
        if 'city' in data:
            raise serializers.ValidationError({
                "city": "This field is not allowed. Use 'package_city' (read-only) instead."
            })
        
        package = data.get('package')
        if package:
            if not data.get('status'):
                data['status'] = package.shipment_status
        return data
