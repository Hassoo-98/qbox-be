from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid
import random


class HomeOwnerManager(BaseUserManager):
    def create_user(self, email, full_name, phone_number=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, full_name, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, full_name, phone_number, password, **extra_fields)


class CustomHomeOwnerAddress(models.Model):
    short_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=60, blank=True)
    district = models.CharField(max_length=60, blank=True)
    street = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    building_number = models.CharField(max_length=20, blank=True)
    secondary_building_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Home Owner Addresses"

    def __str__(self):
        return f"{self.short_address or self.building_number or '—'} — {self.city or '—'}"


class CustomHomeOwner(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    secondary_phone_number = models.CharField(max_length=15, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    email_otp = models.CharField(max_length=6, blank=True, null=True)
    phone_otp = models.CharField(max_length=6, blank=True, null=True)
    password_reset_otp = models.CharField(max_length=6, blank=True, null=True)
    password_reset_otp_expires = models.DateTimeField(blank=True, null=True)

    address = models.OneToOneField(
        CustomHomeOwnerAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="homeowner"
    )

    preferred_installment_location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = HomeOwnerManager()

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))