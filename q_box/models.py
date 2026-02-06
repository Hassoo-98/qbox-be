from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class Qbox(models.Model):
    class Status(models.TextChoices):
        ONLINE = "Online", "Online"
        OFFLINE = "Offline", "Offline"
        ERROR = "Error", "Error"

    class LedIndicator(models.TextChoices):
        GREEN = "Green", "Green"
        RED = "Red", "Red"

    class CameraStatus(models.TextChoices):
        WORKING = "Working", "Working"
        NOT_WORKING = "Not Working", "Not Working"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qbox_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique device identifier (often printed on device)"
    )
    homeowner = models.ForeignKey(
        'home_owner.CustomHomeOwner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qboxes",
        help_text="The current registered owner"
    )
    homeowner_name_snapshot = models.CharField(max_length=100, blank=True)
    short_address_snapshot  = models.CharField(max_length=150, blank=True)
    city_snapshot           = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE
    )

    led_indicator = models.CharField(
        max_length=10,
        choices=LedIndicator.choices,
        default=LedIndicator.GREEN
    )

    camera_status = models.CharField(
        max_length=20,
        choices=CameraStatus.choices,
        default=CameraStatus.WORKING
    )

    last_online     = models.DateTimeField(null=True, blank=True)
    activation_date = models.DateTimeField(default=timezone.now)
    qbox_image = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        if self.homeowner:
            return f"Qbox {self.qbox_id} — {self.homeowner.full_name}"
        return f"Qbox {self.qbox_id} — Unassigned"

    def sync_with_homeowner(self, save=True):
        """
        Updates snapshot fields from the current homeowner.
        Call this after assigning a homeowner or after homeowner profile changes.
        """
        if self.homeowner:
            self.homeowner_name_snapshot = self.homeowner.full_name
            if self.homeowner.address:
                self.short_address_snapshot = (
                    self.homeowner.address.short_address
                    or self.homeowner.address.building_number
                    or self.homeowner.address.street
                    or ""
                )
                self.city_snapshot = self.homeowner.address.city or ""
            else:
                self.short_address_snapshot = ""
                self.city_snapshot = ""
        else:
            self.homeowner_name_snapshot = ""
            self.short_address_snapshot = ""
            self.city_snapshot = ""

        if save:
            self.save(update_fields=[
                'homeowner_name_snapshot',
                'short_address_snapshot',
                'city_snapshot'
            ])

    class Meta:
        verbose_name = "Qbox Device"
        verbose_name_plural = "Qbox Devices"
        ordering = ["-activation_date"]
        indexes = [
            models.Index(fields=['qbox_id']),
            models.Index(fields=['homeowner']),
        ]


class QboxAccessQRCode(models.Model):
    """
    Model for generating temporary access QR codes for a Qbox
    """
    class DurationType(models.TextChoices):
        DAYS = "days", "Days"
        MINUTES = "minutes", "Minutes"

    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        EXPIRED = "Expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qbox = models.ForeignKey(
        Qbox,
        on_delete=models.CASCADE,
        related_name="access_qrcodes",
        help_text="The Qbox this QR code grants access to"
    )
    homeowner = models.ForeignKey(
        'home_owner.CustomHomeOwner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_qrcodes",
        help_text="The homeowner who created this QR code"
    )
    
    # QR Code details
    name = models.CharField(
        max_length=100,
        help_text="Name for this QR code (e.g., 'Morning shift entrance')"
    )
    location = models.CharField(
        max_length=200,
        help_text="Location description (e.g., 'Box Main Entrance')"
    )
    address = models.CharField(
        max_length=500,
        help_text="Full address (e.g., 'National Address 47B')"
    )
    
    # Access limits
    max_users = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of users who can use this QR code"
    )
    current_users = models.PositiveIntegerField(
        default=0,
        help_text="Current number of users who have used this QR code"
    )
    
    # Duration settings
    duration_type = models.CharField(
        max_length=20,
        choices=DurationType.choices,
        default=DurationType.DAYS,
        help_text="Whether valid_duration is in days or minutes"
    )
    valid_duration = models.PositiveIntegerField(
        default=1,
        help_text="Duration value (days or minutes based on duration_type)"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this QR code expires"
    )
    
    # QR Code data (the actual data encoded in the QR)
    access_token = models.CharField(
        max_length=500,
        unique=True,
        help_text="Unique access token encoded in the QR code"
    )
    qr_code_image = models.ImageField(
        upload_to='qrcodes/',
        null=True,
        blank=True,
        help_text="Generated QR code image"
    )
    qr_code_url = models.URLField(
        blank=True,
        default="",
        help_text="URL to the generated QR code image"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this QR code is currently active (manually toggled)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.qbox.qbox_id}"

    def save(self, *args, **kwargs):
        # Generate access token if not set
        if not self.access_token:
            import secrets
            self.access_token = secrets.token_urlsafe(32)
        
        # Calculate expires_at based on duration
        if not self.expires_at:
            if self.duration_type == self.DurationType.DAYS:
                self.expires_at = timezone.now() + timezone.timedelta(days=self.valid_duration)
            else:  # minutes
                self.expires_at = timezone.now() + timezone.timedelta(minutes=self.valid_duration)
        
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the QR code is still valid"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.current_users >= self.max_users:
            return False
        return True

    def increment_usage(self):
        """Increment the usage counter"""
        if self.current_users < self.max_users:
            self.current_users += 1
            self.save(update_fields=['current_users'])
            return True
        return False
    
    def get_status(self):
        """Get the current status of the QR code (Active/Expired)"""
        return self.Status.ACTIVE if self.is_valid() else self.Status.EXPIRED
    
    def get_remaining_users(self):
        """Get remaining users that can use this QR code"""
        return self.max_users - self.current_users
    
    def get_expires_in(self):
        """Get time remaining until expiration"""
        if not self.expires_at:
            return None
        if timezone.now() >= self.expires_at:
            return "Expired"
        delta = self.expires_at - timezone.now()
        if delta.days > 0:
            return f"{delta.days} days"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours"
        else:
            return f"{delta.seconds // 60} minutes"

    class Meta:
        verbose_name = "Qbox Access QR Code"
        verbose_name_plural = "Qbox Access QR Codes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['qbox']),
            models.Index(fields=['access_token']),
            models.Index(fields=['expires_at']),
        ]


class QboxAccessUser(models.Model):
    """
    Model for tracking users who have accessed a Qbox via QR code
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ForeignKey(
        QboxAccessQRCode,
        on_delete=models.CASCADE,
        related_name="access_users",
        help_text="The QR code used for access"
    )
    user_identifier = models.CharField(
        max_length=200,
        help_text="User identifier (email, phone, or custom ID)"
    )
    user_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="User's name if provided"
    )
    accessed_at = models.DateTimeField(auto_now_add=True)
    access_type = models.CharField(
        max_length=50,
        default="qr_code",
        help_text="Type of access (qr_code, manual, etc.)"
    )

    def __str__(self):
        return f"{self.user_identifier} - {self.qr_code.name}"

    class Meta:
        verbose_name = "Qbox Access User"
        verbose_name_plural = "Qbox Access Users"
        ordering = ["-accessed_at"]
