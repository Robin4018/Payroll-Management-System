from rest_framework import serializers
from .models import Attendance, LeaveType, LeaveRequest

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"

class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.ReadOnlyField(source='leave_type.name')
    employee_name = serializers.ReadOnlyField(source='employee.first_name')
    
    class Meta:
        model = LeaveRequest
        fields = "__all__"

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.get_full_name')
    employee_code = serializers.ReadOnlyField(source='employee.employee_code')
    work_duration = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = "__all__"

    def get_work_duration(self, obj):
        if obj.check_in and obj.check_out:
            import datetime
            td = datetime.datetime.combine(datetime.date.min, obj.check_out) - \
                 datetime.datetime.combine(datetime.date.min, obj.check_in)
            return round(td.total_seconds() / 3600, 2)
        return 0

from .models import LeaveBalance
class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.ReadOnlyField(source='leave_type.name')
    
    class Meta:
        model = LeaveBalance
        fields = ['id', 'leave_type', 'leave_type_name', 'balance', 'accrued', 'used']
