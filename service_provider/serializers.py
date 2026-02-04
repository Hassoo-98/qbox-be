from rest_framework import serializers
from .models import ServiceProvider

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'name', 'is_approved', 'business_registration_number',
            'contact_person_name', 'phone_number', 'email', 'operating_cities',
            'settlement_cycle_days', 'markup_type', 'markup_value',
            'monday_open', 'monday_close', 'tuesday_open', 'tuesday_close',
            'wednesday_open', 'wednesday_close', 'thursday_open', 'thursday_close',
            'friday_open', 'friday_close', 'saturday_open', 'saturday_close',
            'sunday_open', 'sunday_close', 'first_kg_charge', 'additional_kg_charge',
            'fuel_surcharge_percentage', 'fuel_surcharge_enabled', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ServiceProviderApprovalSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
