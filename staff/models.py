from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
import uuid
class StaffRole(models.TextChoices):
    SUPERVISOR="supervisor","Supervisor",
    AGENT="agent","Agent"
class CustomStaff(AbstractUser):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=255)
    phone_number=models.CharField(max_length=20)
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=20, choices=StaffRole.choices)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=True)
    groups=models.ManyToManyField(
        'auth.Group',
        related_name='staff_set',
        blank=True
    )
    user_permissions=models.ManyToManyField(
        'auth.Permission',
        related_name='staff_set',
        blank=True
    )
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['name','phone_number',"email","role","is_staff","is_active"]
    def __str__(self):
        return self.email   