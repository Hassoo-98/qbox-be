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