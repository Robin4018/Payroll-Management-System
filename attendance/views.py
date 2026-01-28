from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Attendance, LeaveType, LeaveRequest
from .serializers import AttendanceSerializer, LeaveTypeSerializer, LeaveRequestSerializer

class LeaveTypeViewSet(ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

class LeaveRequestViewSet(ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
        leave_request.save()
        
        # Notify Employee
        if leave_request.employee and leave_request.employee.user:
            from notifications.utils import send_notification
            send_notification(
                user=leave_request.employee.user,
                title="Leave Approved",
                message=f"Your leave for {leave_request.start_date} is approved.",
                notif_type='LEAVE'
            )
        
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.rejection_reason = request.data.get('reason', '')
        leave_request.save()
        
        # Notify Employee
        if leave_request.employee and leave_request.employee.user:
            from notifications.utils import send_notification
            send_notification(
                user=leave_request.employee.user,
                title="Leave Rejected",
                message=f"Your leave for {leave_request.start_date} is rejected. Reason: {leave_request.rejection_reason}",
                notif_type='LEAVE'
            )
            
        return Response({'status': 'rejected'})

from django_filters.rest_framework import DjangoFilterBackend

class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date', 'employee']

    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        data = request.data
        if not isinstance(data, list):
            data = [data]
            
        results = []
        for item in data:
            employee_id = item.get('employee')
            date = item.get('date')
            
            # Try to find existing record
            attendance = Attendance.objects.filter(employee_id=employee_id, date=date).first()
            if attendance:
                serializer = self.get_serializer(attendance, data=item, partial=True)
            else:
                serializer = self.get_serializer(data=item)
                
            if serializer.is_valid():
                serializer.save()
                results.append(serializer.data)
            else:
                return Response({"error": f"Validation failed for {employee_id}", "details": serializer.errors}, status=400)
                
        return Response(results)
