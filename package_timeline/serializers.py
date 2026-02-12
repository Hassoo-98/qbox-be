from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import PackageTimeline
class PackageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model=PackageTimeline
        fields=(
            "date_and_time",
            "status",
            "description",
            "city",
            "package"
        )
        read_only_fields=("date_and_time")
    def validate_status(self,value):
        """
        Field-level valdiation for status field
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("status must be 3 characters or more")
            )
    def validate_city(self,value):
        """
        Field-level valdiation for city field
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("City must be 3 characters or more")
            )
        if not value.isalpha():
            raise serializers.ValidationError(
            _("City must be characters from a to z")
            )
    def validate(self,data):
        """
        Object-level validation
        """
        if not data.get("status"," ") and not data.get("city"):
            raise serializers.ValidationError(
            _("status and city must be required")
            )