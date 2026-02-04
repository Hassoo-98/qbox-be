from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class ServiceProvider(models.Model):
    """
    Service Provider (e.g. logistics / delivery company profile)
    Matches the 'ABC Providers' creation/editing modal
    """
    name = models.CharField(
        max_length=120,
        verbose_name=_("Service Provider Name"),
        help_text="Official/branding name of the provider"
    )
    is_approved=models.BooleanField(
        default=False,
        verbose_name="Serive Provider approve",
        help_text="Service Provider approve"
    )
    
    business_registration_number = models.CharField(
        max_length=50,
        verbose_name=_("Business Registration Number"),
        unique=True,
        help_text="Commercial registration number (CR)"
    )
    
    contact_person_name = models.CharField(
        max_length=100,
        verbose_name=_("Contact Person Name")
    )
    
    phone_number = models.CharField(
        max_length=15,          
        verbose_name=_("Phone Number"),
        help_text="Preferred format: +9665xxxxxxxx or 9665xxxxxxxx"
    )
    
    email = models.EmailField(
        max_length=150,
        verbose_name=_("Email Address"),
        unique=True
    )
    
    operating_cities = models.ManyToManyField(
        'locations.City',       
        verbose_name=_("Operating Cities"),
        related_name="service_providers",
        blank=True,
        help_text="Cities where this provider can deliver"
    )
    settlement_cycle_days = models.PositiveIntegerField(
        default=7,
        verbose_name=_("Settlement Cycle"),
        help_text="Number of days after delivery until payment (e.g. 7, 15, 30)",
        validators=[MinValueValidator(1), MaxValueValidator(90)]
    )
    class MarkupType(models.TextChoices):
        FIXED       = "fixed",       _("Fixed Amount (SAR)")
        PERCENTAGE  = "percentage",  _("Percentage (%)")
    
    markup_type = models.CharField(
        max_length=20,
        choices=MarkupType.choices,
        default=MarkupType.PERCENTAGE,
        verbose_name=_("Markup Type")
    )
    
    markup_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Markup Value"),
        help_text="Value in SAR (fixed) or percent (e.g. 12.5)",
        validators=[MinValueValidator(0)]
    )
    monday_open    = models.TimeField(null=True, blank=True)
    monday_close   = models.TimeField(null=True, blank=True)
    tuesday_open   = models.TimeField(null=True, blank=True)
    tuesday_close  = models.TimeField(null=True, blank=True)
    wednesday_open = models.TimeField(null=True, blank=True)
    wednesday_close= models.TimeField(null=True, blank=True)
    thursday_open  = models.TimeField(null=True, blank=True)
    thursday_close = models.TimeField(null=True, blank=True)
    friday_open    = models.TimeField(null=True, blank=True)   
    friday_close   = models.TimeField(null=True, blank=True)
    saturday_open  = models.TimeField(null=True, blank=True)
    saturday_close = models.TimeField(null=True, blank=True)
    sunday_open    = models.TimeField(null=True, blank=True)
    sunday_close   = models.TimeField(null=True, blank=True)
    first_kg_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_("First KG Charge"),
        help_text="Charge for the first kilogram (SAR)"
    )
    
    additional_kg_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_("Additional KG Charge"),
        help_text="Charge per extra kilogram (SAR)"
    )
    
    fuel_surcharge_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Fuel Surcharge (%)"),
        help_text="Additional percentage applied on total (if enabled)",
        validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    
    fuel_surcharge_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Enable Fuel Surcharge")
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Service Provider")
        verbose_name_plural = _("Service Providers")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name} ({self.business_registration_number})"
