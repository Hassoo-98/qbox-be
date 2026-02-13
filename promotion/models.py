from django.db import models
from django.utils.translation import gettext_lazy as _
import random 
import string
import uuid

def generate_unique_code():
    while True:
        letters = ''.join(random.choices(string.ascii_uppercase, k=10))
        digits = ''.join(random.choices(string.digits, k=6))
        code = f"${letters}{digits}"
        if not Promotion.objects.filter(code=code).exists():
            return code


class MerchantProviderName(models.Model):
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to="merchant_images/", null=True, blank=True)
    
    def __str__(self):
        return self.name


class Promotion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(max_length=20, unique=True, default=generate_unique_code)
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
    merchant_provider_name = models.ForeignKey(
        MerchantProviderName,
        on_delete=models.CASCADE,
        related_name="promotions"
    )
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
