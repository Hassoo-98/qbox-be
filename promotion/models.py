from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from PIL import Image
import os
import random 
import string
import uuid

def generate_unique_code():
    while True:
        letters = ''.join(random.choices(string.ascii_uppercase, k=10))
        digits = ''.join(random.choices(string.digits, k=6))
        code = f"{letters}{digits}"
        if not Promotion.objects.filter(code=code).exists():
            return code

def merchant_img_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    year = instance.created_at.year if instance.created_at else timezone.now().year
    month = instance.created_at.month if instance.created_at else timezone.now().month
    day = instance.created_at.day if instance.created_at else timezone.now().day
    return os.path.join(
        "merchant_promotion_images",
        str(year),
        str(month),
        str(day),
        filename
    )

class Promotion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    class PromotionType(models.TextChoices):
        FLAT = "Flat", _("Flat")
        PERCENTAGE = "Percentage", _("Percentage")
    
    promo_type = models.CharField(
        max_length=20,
        choices=PromotionType.choices,
        default=PromotionType.FLAT
    )
    user_limit = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_provider_name = models.CharField(max_length=100)
    merchant_provider_img = models.ImageField(upload_to=merchant_img_upload_to, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
        super().save(*args, **kwargs)
        if self.merchant_provider_img:
            try:
                img_path = self.merchant_provider_img.path
                img = Image.open(img_path)
                max_size = (1000, 1000)
                img.thumbnail(max_size, Image.ANTIALIAS)
                img.save(img_path, optimize=True, quality=85)
            except Exception as e:
                print(f"Error processing image: {e}")
    
    def __str__(self):
        return self.title
