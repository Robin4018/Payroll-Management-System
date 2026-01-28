from django.contrib import admin
from .models import Employee, UserProfile

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "tenant", "is_active")
    list_filter = ("tenant", "is_active", "employment_type")
    search_fields = ("first_name", "last_name", "email", "phone", "employee_code")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_type', 'organization_name')
    list_filter = ('organization_type',)
    search_fields = ('user__username', 'organization_name')

