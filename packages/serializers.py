from rest_framework import serializers
from .models import Package, PackageDetails
import uuid

class PackageDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageDetails
        fields = ["id", "package_type", "package_size", "package_weight", "summary"]

class PackageSerializer(serializers.ModelSerializer):
    details = PackageDetailsSerializer(read_only=True)
    type = serializers.SerializerMethodField()
    trackingId = serializers.CharField(source="tracking_id")
    courierName = serializers.CharField(source="service_provider")
    lastUpdate = serializers.DateTimeField(source="last_update")
    qrCode = serializers.CharField(source="qr_code")
    status = serializers.CharField(source="outgoing_status")
    phoneNumber = serializers.CharField(source="recipient_phone")
    email = serializers.EmailField(source="recipient_email")
    recepientName = serializers.CharField(source="recipient_name")
    imageUrl = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    paymentSummary = serializers.SerializerMethodField()
    
    class Meta:
        model = Package
        fields = [
            "id", "qbox", "tracking_id", "trackingId", "merchant_name",
            "service_provider", "courierName", "driver_name", "qr_code", "qrCode",
            "package_type", "type", "outgoing_status", "status", "city",
            "shipment_status", "last_update", "lastUpdate", "created_at", 
            "details", "item_value", "recipient_name", "recepientName",
            "recipient_phone", "phoneNumber", "recipient_email", "email",
            "description", "payment_method", "payment_currency", "payment_charges",
            "imageUrl", "attributes", "paymentSummary"
        ]
        read_only_fields = ["id", "created_at", "last_update"]
    
    def get_type(self, obj):
        return f"PACKAGE_TYPE.{obj.package_type.upper()}"
    
    def get_imageUrl(self, obj):
        return "https://example.com/images/packageItem.jpg"
    
    def get_attributes(self, obj):
        attributes = []
        if hasattr(obj, 'details') and obj.details:
            if obj.details.package_type:
                attributes.append({"type": "Package Type", "value": obj.details.package_type})
            if obj.details.package_weight:
                attributes.append({"type": "Package Weight", "value": obj.details.package_weight})
        if hasattr(obj, 'item_value') and obj.item_value:
            attributes.append({"type": "Item Value", "value": str(obj.item_value)})
        if not attributes:
            attributes = [
                {"type": "Package Type", "value": "General"},
                {"type": "Item Value", "value": "0"},
                {"type": "Package Weight", "value": "1 kg"},
            ]
        return attributes
    
    def get_paymentSummary(self, obj):
        if hasattr(obj, 'payment_method') and obj.payment_method:
            return {
                "paymentMethod": obj.payment_method,
                "charges": obj.payment_charges if hasattr(obj, 'payment_charges') and obj.payment_charges else [
                    {"key": "Base delivery fee (First 5 Kg's)", "value": 5},
                    {"key": "Additional per Kg", "value": 10},
                    {"key": "Tax Fuel", "value": 5},
                ],
                "currency": obj.payment_currency if hasattr(obj, 'payment_currency') and obj.payment_currency else "SAR"
            }
        return {
            "paymentMethod": "Apple Pay",
            "charges": [
                {"key": "Base delivery fee (First 5 Kg's)", "value": 5},
                {"key": "Additional per Kg", "value": 10},
                {"key": "Tax Fuel", "value": 5},
            ],
            "currency": "SAR"
        }

class PackageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            "id", "tracking_id", "merchant_name",
            "service_provider", "driver_name",
            "package_type", "outgoing_status", "shipment_status", "created_at"
        ]


class IncomingPackageSerializer(serializers.Serializer):
    """Serializer for incoming package detail response matching frontend requirements"""
    id = serializers.UUIDField()
    trackingId = serializers.CharField(source="tracking_id")
    type = serializers.SerializerMethodField()
    courierName = serializers.CharField(source="service_provider")
    lastUpdate = serializers.DateTimeField(source="last_update")
    qrCode = serializers.CharField(source="qr_code")
    description = serializers.CharField()
    imageUrl = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    def get_type(self, obj):
        return "PACKAGE_TYPE.INCOMING"

    def get_imageUrl(self, obj):
        # Return a default image URL or the actual image if available
        return "https://example.com/images/packageItem.jpg"

    def get_attributes(self, obj):
        """Build attributes list from package details"""
        attributes = []
        
        # Add package type if available
        if hasattr(obj, 'details') and obj.details:
            if obj.details.package_type:
                attributes.append({
                    "type": "Package Type",
                    "value": obj.details.package_type
                })
            if obj.details.package_weight:
                attributes.append({
                    "type": "Package Weight",
                    "value": obj.details.package_weight
                })
        
        # Add item value if available
        if hasattr(obj, 'item_value') and obj.item_value:
            attributes.append({
                "type": "Item Value",
                "value": str(obj.item_value)
            })
        
        # If no details, return default attributes
        if not attributes:
            attributes = [
                {"type": "Package Type", "value": "General"},
                {"type": "Item Value", "value": "0"},
                {"type": "Package Weight", "value": "1 kg"},
            ]
        
        return attributes


class OutgoingPackageSerializer(serializers.Serializer):
    """Serializer for outgoing package detail response matching frontend requirements"""
    id = serializers.UUIDField()
    type = serializers.SerializerMethodField()
    trackingId = serializers.CharField(source="tracking_id")
    courierName = serializers.CharField(source="service_provider")
    lastUpdate = serializers.DateTimeField(source="last_update")
    qrCode = serializers.CharField(source="qr_code")
    status = serializers.CharField(source="outgoing_status")
    phoneNumber = serializers.CharField(source="recipient_phone")
    email = serializers.EmailField(source="recipient_email")
    recepientName = serializers.CharField(source="recipient_name")
    description = serializers.CharField()
    imageUrl = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    paymentSummary = serializers.SerializerMethodField()

    def get_type(self, obj):
        return "PACKAGE_TYPE.OUTGOING"

    def get_imageUrl(self, obj):
        return "https://example.com/images/packageItem.jpg"

    def get_attributes(self, obj):
        """Build attributes list from package details"""
        attributes = []
        
        if hasattr(obj, 'details') and obj.details:
            if obj.details.package_type:
                attributes.append({
                    "type": "Package Type",
                    "value": obj.details.package_type
                })
            if obj.details.package_weight:
                attributes.append({
                    "type": "Package Weight",
                    "value": obj.details.package_weight
                })
        
        if hasattr(obj, 'item_value') and obj.item_value:
            attributes.append({
                "type": "Item Value",
                "value": str(obj.item_value)
            })
        
        if not attributes:
            attributes = [
                {"type": "Package Type", "value": "General"},
                {"type": "Item Value", "value": "0"},
                {"type": "Package Weight", "value": "1 kg"},
            ]
        
        return attributes

    def get_paymentSummary(self, obj):
        """Build payment summary for outgoing packages"""
        # Use payment fields from model if available, otherwise return default
        if hasattr(obj, 'payment_method') and obj.payment_method:
            return {
                "paymentMethod": obj.payment_method,
                "charges": obj.payment_charges if hasattr(obj, 'payment_charges') and obj.payment_charges else [
                    {"key": "Base delivery fee (First 5 Kg's)", "value": 5},
                    {"key": "Additional per Kg", "value": 10},
                    {"key": "Tax Fuel", "value": 5},
                ],
                "currency": obj.payment_currency if hasattr(obj, 'payment_currency') and obj.payment_currency else "SAR"
            }
        return {
            "paymentMethod": "Apple Pay",
            "charges": [
                {"key": "Base delivery fee (First 5 Kg's)", "value": 5},
                {"key": "Additional per Kg", "value": 10},
                {"key": "Tax Fuel", "value": 5},
            ],
            "currency": "SAR"
        }


class DeliveredPackageSerializer(serializers.Serializer):
    """Serializer for delivered package detail response matching frontend requirements"""
    id = serializers.UUIDField()
    type = serializers.SerializerMethodField()
    trackingId = serializers.CharField(source="tracking_id")
    courierName = serializers.CharField(source="service_provider")
    lastUpdate = serializers.DateTimeField(source="last_update")
    qrCode = serializers.CharField(source="qr_code")
    description = serializers.CharField()
    imageUrl = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    def get_type(self, obj):
        return "PACKAGE_TYPE.DELIVERED"

    def get_imageUrl(self, obj):
        return "https://example.com/images/packageItem.jpg"

    def get_attributes(self, obj):
        """Build attributes list from package details"""
        attributes = []
        
        if hasattr(obj, 'details') and obj.details:
            if obj.details.package_type:
                attributes.append({
                    "type": "Package Type",
                    "value": obj.details.package_type
                })
            if obj.details.package_weight:
                attributes.append({
                    "type": "Package Weight",
                    "value": obj.details.package_weight
                })
        
        if hasattr(obj, 'item_value') and obj.item_value:
            attributes.append({
                "type": "Item Value",
                "value": str(obj.item_value)
            })
        
        if not attributes:
            attributes = [
                {"type": "Package Type", "value": "General"},
                {"type": "Item Value", "value": "0"},
                {"type": "Package Weight", "value": "1 kg"},
            ]
        
        return attributes

class PackageCreateSerializer(serializers.ModelSerializer):
    details = PackageDetailsSerializer(required=False)
    
    class Meta:
        model = Package
        fields = [
            "qbox", "tracking_id", "merchant_name",
            "service_provider", "driver_name", "qr_code",
            "package_type", "outgoing_status", "city", 
            "item_value", "recipient_name", "recipient_phone", 
            "recipient_email", "description",
            "payment_method", "payment_currency", "payment_charges",
            "details"
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
    qboxImage = serializers.CharField(max_length=500, required=True, help_text="URL or base64 data URI of the package image (http://..., https://..., or data:image/...;base64,...)")
    packageDescription = serializers.CharField(required=True, help_text="Description of the package")
    packageItemValue = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Value of the package item")
    currency = serializers.CharField(max_length=10, required=True, help_text="Currency code (e.g., SAR)")
    packageWeight = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Weight of the package")
    packageType = serializers.CharField(max_length=50, required=True, help_text="Type of package")
    qBoxId = serializers.CharField(max_length=50, required=True, help_text="QBox ID")
    phone = serializers.CharField(max_length=20, required=True, help_text="Contact phone number")
    email = serializers.EmailField(required=True, help_text="Contact email")
    fullName = serializers.CharField(max_length=100, required=True, help_text="Full name of the sender")

    def validate_qboxImage(self, value):
        """Handle image URL or base64 from JSON input"""
        if not value:
            return value
        
        # Check for local file paths (mobile devices)
        if isinstance(value, str) and value.startswith('file://'):
            raise serializers.ValidationError(
                "Local file paths (file://) cannot be accessed from the server. "
                "Please either: (1) Convert the image to base64 format, or "
                "(2) Upload the file using multipart/form-data."
            )
        
        if isinstance(value, str):
            if value.startswith('http://') or value.startswith('https://'):
                # Store HTTP URLs directly
                return value
            elif value.startswith('data:image'):
                # Handle base64 data URI - return as-is for URLField storage
                # This makes the image accessible as a data URL
                return value
        
        return value

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
        
        # Extract package image
        package_image = validated_data.pop('qboxImage', '')
        
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
            description=validated_data.pop('packageDescription', ''),
            package_image=package_image,
            # Store additional info in city field as it's not used for outgoing
            city=f"Value: {validated_data.pop('packageItemValue', '')} {validated_data.pop('currency', '')}",
        )
        return package


class ReturnPackageSerializer(serializers.Serializer):
    """Serializer for creating a Return Package with camelCase field names"""
    returnPackageImage = serializers.CharField(max_length=500, required=True, help_text="URL or base64 data URI of the return package image (http://..., https://..., or data:image/...;base64,...)")
    packageDescription = serializers.CharField(required=True, help_text="Description of the return package")
    packageItemValue = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Value of the package item")
    currency = serializers.CharField(max_length=10, required=True, help_text="Currency code (e.g., SAR)")
    packageWeight = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Weight of the package")
    packageType = serializers.CharField(max_length=50, required=True, help_text="Type of package")
    pinCode = serializers.CharField(max_length=20, required=True, help_text="PIN code for return")

    def validate_returnPackageImage(self, value):
        """Handle image URL or base64 from JSON input"""
        if not value:
            return value
        
        # Check for local file paths (mobile devices)
        if isinstance(value, str) and value.startswith('file://'):
            raise serializers.ValidationError(
                "Local file paths (file://) cannot be accessed from the server. "
                "Please either: (1) Convert the image to base64 format, or "
                "(2) Upload the file using multipart/form-data."
            )
        
        if isinstance(value, str):
            if value.startswith('http://') or value.startswith('https://'):
                # Store HTTP URLs directly
                return value
            elif value.startswith('data:image'):
                # Handle base64 data URI - return as-is for URLField storage
                # This makes the image accessible as a data URL
                return value
        
        return value

    def create(self, validated_data):
        """Create a new outgoing package with 'Return' status"""
        # Extract package image
        package_image = validated_data.pop('returnPackageImage', '')
        
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
            description=validated_data.pop('packageDescription', ''),
            package_image=package_image,
            # Store PIN code in driver_name field as it's not used for return packages
            driver_name=f"PIN: {validated_data.pop('pinCode', '')}",
            # Store package value and currency in city field as it's not used for outgoing
            city=f"Value: {validated_data.pop('packageItemValue', '')} {validated_data.pop('currency', '')}",
        )
        return package


class OutgoingPackageSerializer(serializers.ModelSerializer):
    """Serializer for Outgoing packages (both Send and Return) with camelCase field names"""
    details = PackageDetailsSerializer(read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'tracking_id', 'service_provider', 'qbox', 
            'outgoing_status', 'shipment_status', 'created_at', 
            'last_update', 'details', 'merchant_name', 'driver_name', 'city'
        ]


class SendPackageResponseSerializer(serializers.ModelSerializer):
    """Serializer for Send Package response with camelCase field names matching the payload"""
    details = PackageDetailsSerializer(read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'tracking_id', 'merchant_name', 'service_provider', 
            'driver_name', 'outgoing_status', 'shipment_status', 
            'created_at', 'last_update', 'details', 'city', 'qbox'
        ]
    
    def to_representation(self, instance):
        """Convert snake_case to camelCase for the response"""
        data = super().to_representation(instance)
        camel_case_data = {
            'id': data.get('id'),
            'trackingId': data.get('tracking_id'),
            'merchantName': data.get('merchant_name'),
            'serviceProvider': data.get('service_provider'),
            'driverName': data.get('driver_name'),
            'outgoingStatus': data.get('outgoing_status'),
            'shipmentStatus': data.get('shipment_status'),
            'createdAt': data.get('created_at'),
            'lastUpdate': data.get('last_update'),
            'packageType': data.get('details', {}).get('package_type') if data.get('details') else None,
            'packageWeight': data.get('details', {}).get('package_weight') if data.get('details') else None,
            'qboxImage': data.get('city') if data.get('city') and data.get('city').startswith('file://') else None,
            'packageDescription': data.get('city') if data.get('city') and not data.get('city').startswith('file://') else None,
            'packageItemValue': data.get('city').split()[1] if data.get('city') and len(data.get('city', '').split()) > 1 else None,
            'currency': data.get('city').split()[2] if data.get('city') and len(data.get('city', '').split()) > 2 else None,
        }
        
        return camel_case_data


class ReturnPackageResponseSerializer(serializers.ModelSerializer):
    """Serializer for Return Package response with camelCase field names matching the payload"""
    details = PackageDetailsSerializer(read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'tracking_id', 'merchant_name', 
            'outgoing_status', 'shipment_status', 
            'created_at', 'last_update', 'details', 'driver_name', 'city'
        ]
    
    def to_representation(self, instance):
        """Convert snake_case to camelCase for the response"""
        data = super().to_representation(instance)
        pin_code = None
        if data.get('driver_name') and data.get('driver_name', '').startswith('PIN: '):
            pin_code = data.get('driver_name', '').replace('PIN: ', '')
        camel_case_data = {
            'id': data.get('id'),
            'trackingId': data.get('tracking_id'),
            'merchantName': data.get('merchant_name'),
            'outgoingStatus': data.get('outgoing_status'),
            'shipmentStatus': data.get('shipment_status'),
            'createdAt': data.get('created_at'),
            'lastUpdate': data.get('last_update'),
            'packageType': data.get('details', {}).get('package_type') if data.get('details') else None,
            'packageWeight': data.get('details', {}).get('package_weight') if data.get('details') else None,
            'pinCode': pin_code,
            'returnPackageImage': data.get('city') if data.get('city') and data.get('city').startswith('file://') else None,
            'packageDescription': data.get('city') if data.get('city') and not data.get('city').startswith('file://') else None,
            'packageItemValue': data.get('city').split()[1] if data.get('city') and len(data.get('city', '').split()) > 1 else None,
            'currency': data.get('city').split()[2] if data.get('city') and len(data.get('city', '').split()) > 2 else None,
        }
        
        return camel_case_data
