from django.contrib import admin
from .models import Attendance, LeaveType, LeaveRequest, LeaveBalance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in', 'check_out')
    list_filter = ('date', 'status', 'employee__tenant')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_code')

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'max_days_allowed', 'is_paid')
    list_filter = ('tenant', 'is_paid')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type', 'employee__tenant')
    search_fields = ('employee__first_name', 'employee__last_name')

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'balance', 'accrued', 'used')
    list_filter = ('leave_type', 'employee__tenant')
    search_fields = ('employee__first_name', 'employee__last_name')
