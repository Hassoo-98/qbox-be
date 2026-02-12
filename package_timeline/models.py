from django.db import models
from django.utils.translation import gettext_lazy as _
from packages.models import Package
import uuid

class PackageTimeline(models.Model):
    id=models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    date_and_time=models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date and Time"))
    status=models.CharField(max_length=100,verbose_name=_("Status"))
    description=models.TextField(verbose_name=_("Description"))
    city=models.CharField(max_length=100,verbose_name=_("City"))
    package=models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="timeline",
        verbose_name=("Package")
    )
    class Meta:
     ordering=["-date_and_time"]
     verbose_name=_("Package Timeline")
     verbose_name_plural=_("Package Timelines")
    
    def __str__(self):
        return f"{self.status} - {self.package}"
