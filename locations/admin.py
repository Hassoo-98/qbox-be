from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_ar', 'code']
