from rest_framework import serializers
from driver.models import CustomDriver
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomDriver
        fields=[
            "id",
            "image",
            "driver_name",
            "phone_number",
            "email",
            "is_active",
            "is_driver",
            "total_deliveries",
            "success_rate",
            "accessed_at",
    
        ]
        read_only_fields=[
            "id",
            "accessed_at",
            "is_driver"
        ]
        extra_kwargs={
            "phone_number":{"required":True},
            "driver_name":{"required":True},
            "email":{"required":True},
            "image":{"required":True},  
        }
class DriverCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    image = serializers.URLField(max_length=500, required=True)
    driver_name = serializers.CharField(max_length=255, required=True)
    phone_number = serializers.CharField(max_length=10, min_length=10, required=True)
    email = serializers.EmailField(max_length=254, required=True)
    
    class Meta:
        model=CustomDriver
        fields=[
            "username",
            "image",
            "driver_name",
            "phone_number",
            "email",
            "is_active"
        ]
        def create(self,validated_data):
            if not validated_data.get('username'):
                email = validated_data.get('email', '')
                base_username = email.split('@')[0] if email else validated_data.get('driver_name', 'driver').replace(' ', '_')
                username = base_username[:100]  
                counter = 1
                while CustomDriver.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"[:100]
                    counter += 1
                validated_data['username'] = username
            else:
    
                validated_data['username'] = validated_data['username'][:100]
            
            validated_data['password'] = validated_data.get('password', 'driver123!')
            driver=CustomDriver.objects.create(**validated_data)
            return driver
class DriverUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomDriver
        fields=[
            "image",
            "driver_name",
            "phone_number",
            "email",
            "is_active",
        ]
        extra_kwargs={
            "phone_number":{"required":True},
            "driver_name":{"required":True},
            "email":{"required":True},
            "image":{"required":True},
            "is_active":{"required":True}
        }

class DriverStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomDriver
        fields=[
            "is_active"
        ]
        extra_kwargs={
            "is_active":{"required":True}
        }