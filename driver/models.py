from django.contrib.auth.models import AbstractUser,BaseUserManager
import uuid
from django.db import models
class CustomDriver(AbstractUser):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    image = models.URLField(max_length=500, null=True, blank=True)
    driver_name=models.CharField(max_length=255)
    phone_number=models.CharField(max_length=10)
    email=models.EmailField(unique=True)
    is_driver=models.BooleanField(default=True)
    total_deliveries=models.IntegerField(default=0)
    success_rate=models.FloatField(default=0.0)
    accessed_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    groups=models.ManyToManyField(
        'auth.Group',
        related_name='driver_set',
        blank=True
    )
    user_permissions=models.ManyToManyField(
        'auth.Permission',
        related_name='driver_set',
        blank=True
    )
    required_fields=["image","driver_name","phone_number","email","is_active","is_driver",
                     "total_deliveries","success_rate","accessed_at","is_active"]

