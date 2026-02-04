from rest_framework import serializers
from .models import City, Area


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'name_ar', 'code', 'is_active']
        read_only_fields = ['id']


class CityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'name_ar', 'code', 'is_active']


class CityStatusUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)


class AreaSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = Area
        fields = ['id', 'name', 'city', 'city_name', 'is_active']
        read_only_fields = ['id', 'city_name']


class AreaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['name', 'city', 'is_active']


class AreaStatusUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)
