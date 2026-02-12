from django.db import models
from django.utils import timezone
import uuid

class PackageDetails(models.Model):
    package_type = models.CharField(
        max_length=50,         
        blank=True
    )
    package_size = models.CharField(
        max_length=50,        
        blank=True
    )
    package_weight = models.CharField(
        max_length=30,      
        blank=True
    )
    class Meta:
        verbose_name_plural = "Package Details"
    def __str__(self):
        return f"{self.package_type or '?'} - {self.package_size or '?'} - {self.package_weight or '?'}"
    @property
    def summary(self):
        parts = [self.package_type, self.package_size, self.package_weight]
        return " / ".join(filter(None, parts)) or "No details"


class Package(models.Model):
    class PackageType(models.TextChoices):
        INCOMING = "Incoming", "Incoming"
        OUTGOING = "Outgoing", "Outgoing"
        DELIVERED = "Delivered", "Delivered"

    class OutgoingStatus(models.TextChoices):
        SENT = "Sent", "Sent"
        RETURNED = "Return", "Return"

    class ShipmentStatus(models.TextChoices):
        SHIPMENT_CREATED    = "Shipment-Created",    "Shipment Created"
        OUT_FOR_PICKUP      = "Out-for-Pickup",      "Out for Pickup"
        PICKUP_COMPLETED    = "Pickup-Completed",    "Pickup Completed"
        PICKUP_FAILED       = "Pickup-Failed",       "Pickup Failed"
        OUT_FOR_DELIVERY    = "Out-for-Delivery",    "Out for Delivery"
        ISSUE_LOGGED        = "Issue-Logged",        "Issue Logged"
        DELIVERY_COMPLETED  = "Delivery-Completed",  "Delivery Completed"
        DELIVERY_FAILED     = "Delivery-Failed",     "Delivery Failed"
        RETURN_COMPLETED    = "Return-Completed",    "Return Completed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    qbox = models.ForeignKey(
        'q_box.Qbox',                     
        on_delete=models.SET_NULL,          
        null=True,
        blank=True,
        related_name="packages",
        help_text="The Qbox this package is currently associated with / delivered to"
    )

    tracking_id = models.CharField(
        max_length=20,              
        unique=True,
        db_index=True,
        help_text="Unique tracking number"
    )

    merchant_name = models.CharField(
        max_length=100,
        blank=True
    )

    service_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text="Courier / logistics company (Aramex, DHL, local provider...)"
    )

    driver_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of driver currently assigned (if any)"
    )

    qr_code = models.CharField(
        max_length=100,             
        blank=True,
        help_text="QR code value or URL"
    )
    
    package_type = models.CharField(
        max_length=20,
        choices=PackageType.choices,
        default=PackageType.INCOMING,
        help_text="Type of package: Incoming, Outgoing, or Delivered"
    )
    
    outgoing_status = models.CharField(
        max_length=20,
        choices=OutgoingStatus.choices,
        blank=True,
        null=True,
        help_text="Status for Outgoing packages: Sent or Return"
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City name (required for Incoming packages)"
    )

    item_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Value of the item in the package"
    )

    # Outgoing package fields
    recipient_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Recipient name for outgoing packages"
    )
    recipient_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Recipient phone number"
    )
    recipient_email = models.EmailField(
        blank=True,
        help_text="Recipient email address"
    )

    description = models.TextField(
        blank=True,
        help_text="Package description"
    )

    # Payment fields for outgoing packages
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        default="Apple Pay",
        help_text="Payment method for outgoing packages"
    )
    payment_currency = models.CharField(
        max_length=10,
        blank=True,
        default="SAR",
        help_text="Payment currency"
    )
    payment_charges = models.JSONField(
        default=list,
        blank=True,
        help_text="Payment charges as JSON array"
    )

    shipment_status = models.CharField(
        max_length=30,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.SHIPMENT_CREATED
    )
    last_update = models.DateTimeField(
        auto_now=True,          
        help_text="Last time any field was changed"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )
    details = models.OneToOneField(
        PackageDetails,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="package"
    )

    def __str__(self):
        qbox_str = f" → Qbox {self.qbox.qbox_id}" if self.qbox else ""
        return f"Package {self.tracking_id} ({self.shipment_status}){qbox_str}"

    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tracking_id"]),
            models.Index(fields=["qbox"]),
            models.Index(fields=["shipment_status"]),
            models.Index(fields=["package_type"]),
        ]
