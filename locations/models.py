from django.db import models
from django.utils.translation import gettext_lazy as _


class City(models.Model):
    """
    City model for operating cities of service providers
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("City Name")
    )
    name_ar = models.CharField(
        max_length=100,
        verbose_name=_("Arabic City Name"),
        blank=True,
        null=True
    )
    code = models.CharField(
        max_length=10,
        verbose_name=_("City Code"),
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ['name']

    def __str__(self):
        return self.name
