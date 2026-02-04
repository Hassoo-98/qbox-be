from rest_framework import serializers
from staff.models import CustomStaff

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomStaff
        fields = [
            'id',
            'name',
            'phone_number',
            'email',
            'role',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login'
        ]

class StaffCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomStaff
        fields = [
            'name',
            'phone_number',
            'email',
            'role',
            'password',
            'is_active',
            'is_staff',
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email', '')
        username = email.split('@')[0] if email else f"staff_{validated_data.get('name', '').replace(' ', '_')}"
        base_username = username
        counter = 1
        while CustomStaff.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        staff = CustomStaff.objects.create_user(
            username=username,
            **validated_data,
            password=password
        )
        return staff

class StaffUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomStaff
        fields = [
            'name',
            'phone_number',
            'role',
            'is_active',
            'is_staff',
            'password',
            'email'
        ]

class StaffStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomStaff
        fields = ['is_active']
