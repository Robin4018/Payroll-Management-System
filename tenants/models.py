from django.db import models

class Tenant(models.Model):
    class TenantType(models.TextChoices):
        EDUCATION = 'EDUCATION', 'Education'
        CORPORATE = 'CORPORATE', 'Corporate'

    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=50, blank=True, help_text="Abbreviation for sidebar/mobile")
    type = models.CharField(
        max_length=20, 
        choices=TenantType.choices, 
        default=TenantType.CORPORATE
    )
    financial_year_start = models.DateField(null=True, blank=True, help_text="e.g., April 1st or June 1st")
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True)
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    # Configuration
    salary_cycle_start_day = models.PositiveIntegerField(default=1, help_text="Day of month when cycle starts")
    tax_slabs = models.JSONField(default=dict, blank=True, help_text="JSON structure for tax slabs")
    
    # Geofencing Configuration
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="College center latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="College center longitude")
    geofence_radius = models.PositiveIntegerField(default=200, help_text="Allowed radius in meters")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
