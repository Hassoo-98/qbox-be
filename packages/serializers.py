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
            "package_type", "outgoing_status", "city",
            "shipment_status", "last_update", "created_at", "details"
        ]
        read_only_fields = ["id", "created_at", "last_update"]

class PackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            "id", "tracking_id", "merchant_name",
            "service_provider", "driver_name",
            "package_type", "outgoing_status", "shipment_status", "created_at"
        ]

class PackageCreateSerializer(serializers.ModelSerializer):
    details = PackageDetailsSerializer(required=False)
    
    class Meta:
        model = Package
        fields = [
            "qbox", "tracking_id", "merchant_name",
            "service_provider", "driver_name", "qr_code",
            "package_type", "outgoing_status", "city", "details"
        ]
        extra_kwargs = {
            "tracking_id": {"required": False, "allow_blank": True}
        }

    def validate(self, data):
        """
        Validate fields based on package type:
        - Incoming: city is required, outgoing_status should not be set
        - Outgoing: outgoing_status is required (Sent or Return)
        - Delivered: no special requirements
        """
        package_type = data.get('package_type', 'Incoming')
        
        if package_type == 'Incoming':
            if not data.get('city'):
                raise serializers.ValidationError({
                    "city": "City is required for Incoming packages."
                })
            if data.get('outgoing_status'):
                raise serializers.ValidationError({
                    "outgoing_status": "Outgoing status should not be set for Incoming packages."
                })
        
        elif package_type == 'Outgoing':
            if not data.get('outgoing_status'):
                raise serializers.ValidationError({
                    "outgoing_status": "Outgoing status (Sent or Return) is required for Outgoing packages."
                })
        
        # Delivered packages have no special requirements
        
        return data

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
            "package_type", "outgoing_status", "city", "shipment_status", "details"
        ]

    def validate(self, data):
        """
        Validate fields based on package type during update:
        - Incoming: city is required, outgoing_status should not be set
        - Outgoing: outgoing_status is required (Sent or Return)
        """
        package_type = data.get('package_type', getattr(self.instance, 'package_type', 'Incoming'))
        
        if package_type == 'Incoming':
            if not data.get('city') and not getattr(self.instance, 'city', None):
                raise serializers.ValidationError({
                    "city": "City is required for Incoming packages."
                })
            if data.get('outgoing_status'):
                raise serializers.ValidationError({
                    "outgoing_status": "Outgoing status should not be set for Incoming packages."
                })
        
        elif package_type == 'Outgoing':
            if not data.get('outgoing_status') and not getattr(self.instance, 'outgoing_status', None):
                raise serializers.ValidationError({
                    "outgoing_status": "Outgoing status (Sent or Return) is required for Outgoing packages."
                })
        
        return data

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
    package_type = serializers.ChoiceField(
        choices=Package.PackageType.choices, 
        required=True,
        help_text="Package type: Incoming, Outgoing, or Delivered"
    )
    outgoing_status = serializers.ChoiceField(
        choices=Package.OutgoingStatus.choices,
        required=False,
        allow_null=True,
        help_text="Outgoing status (Sent or Return) - required only for Outgoing packages"
    )
    city = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="City name - required for Incoming packages"
    )
    is_active = serializers.BooleanField(required=True)

    def validate(self, data):
        """
        Validate based on package type.
        """
        package_type = data.get('package_type')
        
        if package_type == 'Incoming':
            if not data.get('city'):
                raise serializers.ValidationError({
                    "city": "City is required when updating to Incoming type."
                })
            if data.get('outgoing_status'):
                raise serializers.ValidationError({
                    "outgoing_status": "Outgoing status cannot be set for Incoming packages."
                })
        
        elif package_type == 'Outgoing':
            if not data.get('outgoing_status'):
                raise serializers.ValidationError({
                    "outgoing_status": "Outgoing status (Sent or Return) is required for Outgoing packages."
                })
        
        return data


class SendPackageSerializer(serializers.Serializer):
    """Serializer for creating a Send Package with camelCase field names"""
    shippingCompany = serializers.CharField(max_length=100, required=True, help_text="Shipping company name")
    qboxImage = serializers.CharField(max_length=500, required=True, help_text="URL or file path of the package image")
    packageDescription = serializers.CharField(required=True, help_text="Description of the package")
    packageItemValue = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Value of the package item")
    currency = serializers.CharField(max_length=10, required=True, help_text="Currency code (e.g., SAR)")
    packageWeight = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Weight of the package")
    packageType = serializers.CharField(max_length=50, required=True, help_text="Type of package")
    qBoxId = serializers.CharField(max_length=50, required=True, help_text="QBox ID")
    phone = serializers.CharField(max_length=20, required=True, help_text="Contact phone number")
    email = serializers.EmailField(required=True, help_text="Contact email")
    fullName = serializers.CharField(max_length=100, required=True, help_text="Full name of the sender")

    def create(self, validated_data):
        """Create a new outgoing package with 'Sent' status"""
        from q_box.models import Qbox
        
        # Extract QBox ID and get the QBox object
        qbox_id = validated_data.pop('qBoxId', None)
        qbox = None
        if qbox_id:
            try:
                qbox = Qbox.objects.get(qbox_id=qbox_id)
            except Qbox.DoesNotExist:
                pass
        
        # Create PackageDetails for the package
        details_data = {
            'package_type': validated_data.pop('packageType', ''),
            'package_weight': str(validated_data.pop('packageWeight', '')),
        }
        details = PackageDetails.objects.create(**details_data)
        
        # Auto-generate tracking_id
        tracking_id = f"SND-{str(uuid.uuid4())[:8].upper()}"
        
        # Create the package as Outgoing with Sent status
        package = Package.objects.create(
            tracking_id=tracking_id,
            merchant_name=validated_data.pop('fullName', ''),
            service_provider=validated_data.pop('shippingCompany', ''),
            outgoing_status='Sent',
            package_type='Outgoing',
            shipment_status=Package.ShipmentStatus.SHIPMENT_CREATED,
            details=details,
            qbox=qbox,
            driver_name=validated_data.pop('fullName', ''),
            # Store additional info in city field as it's not used for outgoing
            city=f"Value: {validated_data.pop('packageItemValue', '')} {validated_data.pop('currency', '')}",
        )
        return package


class ReturnPackageSerializer(serializers.Serializer):
    """Serializer for creating a Return Package with camelCase field names"""
    returnPackageImage = serializers.CharField(max_length=500, required=True, help_text="URL or file path of the return package image")
    packageDescription = serializers.CharField(required=True, help_text="Description of the return package")
    packageItemValue = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Value of the package item")
    currency = serializers.CharField(max_length=10, required=True, help_text="Currency code (e.g., SAR)")
    packageWeight = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Weight of the package")
    packageType = serializers.CharField(max_length=50, required=True, help_text="Type of package")
    pinCode = serializers.CharField(max_length=20, required=True, help_text="PIN code for return")

    def create(self, validated_data):
        """Create a new outgoing package with 'Return' status"""
        # Create PackageDetails for the package
        details_data = {
            'package_type': validated_data.pop('packageType', ''),
            'package_weight': str(validated_data.pop('packageWeight', '')),
        }
        details = PackageDetails.objects.create(**details_data)
        
        # Auto-generate tracking_id
        tracking_id = f"RET-{str(uuid.uuid4())[:8].upper()}"
        
        # Create the package as Outgoing with Return status
        package = Package.objects.create(
            tracking_id=tracking_id,
            outgoing_status='Return',
            package_type='Outgoing',
            shipment_status=Package.ShipmentStatus.SHIPMENT_CREATED,
            details=details,
            # Store PIN code in driver_name field as it's not used for return packages
            driver_name=f"PIN: {validated_data.pop('pinCode', '')}",
            # Store package value and currency in city field as it's not used for outgoing
            city=f"Value: {validated_data.pop('packageItemValue', '')} {validated_data.pop('currency', '')}",
        )
        return package


class OutgoingPackageSerializer(serializers.ModelSerializer):
    """Serializer for Outgoing packages (both Send and Return)"""
    details = PackageDetailsSerializer(read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'tracking_id', 'service_provider', 'qbox', 
            'outgoing_status', 'shipment_status', 'created_at', 
            'last_update', 'details'
        ]
