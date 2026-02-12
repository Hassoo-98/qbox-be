from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import PackageTimeline
class PackageTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model=PackageTimeline
        fields=(
            "id",
            "date_and_time",
            "status",
            "description",
            "city",
            "package"
        )
        read_only_fields=["date_and_time"]
    def validate_status(self,value):
        """
        Field-level valdiation for status field
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("status must be 3 characters or more")
            )
        return value
    def validate_city(self,value):
        """
        Field-level valdiation for city field
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("City must be 3 characters or more")
            )
        return value
