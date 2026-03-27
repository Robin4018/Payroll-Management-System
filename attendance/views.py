from django.utils import timezone
from datetime import date
from django.db.models import Count
import math
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Attendance, LeaveType, LeaveRequest, LeaveBalance
from .serializers import AttendanceSerializer, LeaveTypeSerializer, LeaveRequestSerializer, LeaveBalanceSerializer
import base64
from django.core.files.base import ContentFile
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None

def calculate_distance(lat1, lon1, lat2, lon2):
    # Ensure all inputs are floats before calculation
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    
    # R = Earth radius in meters
    R = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) * math.sin(dp / 2) + \
        math.cos(p1) * math.cos(p2) * \
        math.sin(dl / 2) * math.sin(dl / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class LeaveTypeViewSet(ModelViewSet):
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return LeaveType.objects.filter(tenant=user.employee.tenant)
        
        if hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            return LeaveType.objects.filter(tenant__type=tenant_type)
            
        return LeaveType.objects.all()

class LeaveBalanceViewSet(ModelViewSet):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get'] # Read-only for staff mostly

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee'):
            return LeaveBalance.objects.filter(employee=user.employee)
        return LeaveBalance.objects.none()

class LeaveRequestViewSet(ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'status', 'leave_type']

    def get_queryset(self):
        user = self.request.user
        qs = LeaveRequest.objects.all().order_by('-created_at')
        
        # 1. Tenant Isolation
        if hasattr(user, 'employee') and user.employee.tenant:
            qs = qs.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            qs = qs.filter(employee__tenant__type=tenant_type)
            
        # 2. Staff View Restriction
        is_admin = user.is_superuser or user.is_staff or (hasattr(user, 'employee') and user.user.groups.filter(name='Admin').exists())
        if not is_admin and hasattr(user, 'employee'):
            qs = qs.filter(employee=user.employee)
                
        return qs

    def perform_create(self, serializer):
        leave_request = serializer.save()
        
        # Notify Admins
        from notifications.utils import notify_admins
        notify_admins(
            title="New Leave Request",
            message=f"{leave_request.employee.first_name} {leave_request.employee.last_name} has requested leave from {leave_request.start_date} to {leave_request.end_date}.",
            notif_type='LEAVE'
        )

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



class AttendanceViewSet(ModelViewSet):
    # queryset = Attendance.objects.all()  # Removed in favor of get_queryset
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date', 'employee']

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.all().order_by('-date')
        
        # 1. Tenant Isolation
        if hasattr(user, 'employee') and user.employee.tenant:
            qs = qs.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            qs = qs.filter(employee__tenant__type=tenant_type)
        
        # 2. Permission Restriction: Staff see ONLY their records
        is_admin = user.is_superuser or user.is_staff or (hasattr(user, 'employee') and user.groups.filter(name='Admin').exists())
        
        if not is_admin and hasattr(user, 'employee'):
            qs = qs.filter(employee=user.employee)
            
        return qs

    @action(detail=False, methods=['GET'])
    def export_csv(self, request):
        import csv
        from django.http import HttpResponse
        
        date_str = request.query_params.get('date')
        qs = self.get_queryset()
        if date_str:
            qs = qs.filter(date=date_str)

        response = HttpResponse(content_type='text/csv')
        filename = f"attendance_{date_str}.csv" if date_str else "attendance_all.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Employee Name', 'Employee Code', 'Check In', 'Check Out', 'Status'])
        
        for record in qs:
            writer.writerow([
                record.date,
                record.employee.get_full_name(),
                record.employee.employee_code,
                record.check_in,
                record.check_out,
                record.status
            ])
        
        return response

    @action(detail=False, methods=['get'], url_path='daily_summary')
    def daily_summary(self, request):
        date_str = request.query_params.get('date', timezone.now().date().isoformat())
        user = request.user
        
        # Determine tenant
        tenant = None
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first()

        if not tenant:
            return Response({"error": "No tenant found"}, status=400)

        total_employees = Employee.objects.filter(tenant=tenant, is_active=True).count()
        attendance_qs = Attendance.objects.filter(employee__tenant=tenant, date=date_str)
        
        present = attendance_qs.filter(status=Attendance.Status.PRESENT).count()
        leave = attendance_qs.filter(status=Attendance.Status.LEAVE).count()
        half_day = attendance_qs.filter(status=Attendance.Status.HALF_DAY).count()
        
        # Geofence violations (hypothetical, if we tracked them)
        # For now, let's assume we don't have a direct field, or use a threshold
        violations = 0 

        return Response({
            "total": total_employees,
            "present": present,
            "leave": leave,
            "half_day": half_day,
            "absent": max(0, total_employees - (present + leave + half_day)),
            "violations": violations
        })

    @action(detail=False, methods=['get'], url_path='my_summary')
    def my_summary(self, request):
        if not hasattr(request.user, 'employee'):
            return Response({"error": "No employee profile found"}, status=404)
        
        employee = request.user.employee
        now = timezone.localtime()
        today = now.date()
        
        # Today's status
        today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
        today_status = today_attendance.status if today_attendance else "NOT_MARKED"
        
        # Current month presence
        current_month = today.month
        current_year = today.year
        presence_count = Attendance.objects.filter(
            employee=employee, 
            date__month=current_month, 
            date__year=current_year,
            status=Attendance.Status.PRESENT
        ).count()
        
        tenant = employee.tenant
        
        return Response({
            "today_status": today_status,
            "presence_count": presence_count,
            "check_in": today_attendance.check_in if today_attendance else None,
            "check_out": today_attendance.check_out if today_attendance else None,
            "geofence": {
                "latitude": tenant.latitude,
                "longitude": tenant.longitude,
                "radius": tenant.geofence_radius
            }
        })

    @action(detail=False, methods=['post'], url_path='mark_attendance')
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
    @action(detail=False, methods=['post'], url_path='geo_check_in')
    def geo_check_in(self, request):
        try:
            if not hasattr(request.user, 'employee'):
                return Response({"error": "No employee profile found"}, status=404)
            
            employee = request.user.employee
            tenant = employee.tenant
            
            if not tenant or not tenant.latitude or not tenant.longitude:
                return Response({"error": "Geofencing not configured for this college"}, status=400)
                
            lat = request.data.get('latitude')
            lon = request.data.get('longitude')
            action_type = request.data.get('action') # 'check_in' or 'check_out'
            
            if lat is None or lon is None:
                return Response({"error": "Latitude and longitude required"}, status=400)
                
            distance = calculate_distance(lat, lon, tenant.latitude, tenant.longitude)
            
            if distance > tenant.geofence_radius:
                return Response({
                    "error": "Out of range", 
                    "distance": round(distance, 2),
                    "required": tenant.geofence_radius
                }, status=403)
                
            now = timezone.localtime()
            today = now.date()
            current_time = now.time()
            
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={'status': Attendance.Status.PRESENT}
            )
            
            if action_type == 'check_in':
                if attendance.check_in:
                     return Response({"error": "Already checked in"}, status=400)
                
                # Face Recognition Logic
                face_image_b64 = request.data.get('face_image')
                if not face_image_b64:
                    return Response({"error": "Face capture required for attendance"}, status=400)
                
                try:
                    # Remove header if present
                    if 'base64,' in face_image_b64:
                        face_image_b64 = face_image_b64.split('base64,')[1]
                    
                    header, data = "data:image/jpeg;base64", face_image_b64
                    img_data = base64.b64decode(data)
                    
                    # Face Detection (Verification)
                    if cv2:
                        nparr = np.frombuffer(img_data, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        
                        # Load pre-trained face detector
                        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                        
                        if len(faces) == 0:
                             return Response({"error": "No face detected. Please ensure your face is clearly visible."}, status=400)
                    
                    # Save the image
                    file_name = f"attendance_{employee.id}_{today}_in.jpg"
                    attendance.face_image_check_in.save(file_name, ContentFile(img_data), save=False)
                    
                except Exception as fe:
                    return Response({"error": f"Face processing failed: {str(fe)}"}, status=400)
                    
                attendance.check_in = current_time
                attendance.status = Attendance.Status.PRESENT
            elif action_type == 'check_out':
                if not attendance.check_in:
                    return Response({"error": "Please check in first"}, status=400)
                
                # Face capture on check out too
                face_image_b64 = request.data.get('face_image')
                if face_image_b64:
                    try:
                        if 'base64,' in face_image_b64:
                            face_image_b64 = face_image_b64.split('base64,')[1]
                        img_data = base64.b64decode(face_image_b64)
                        file_name = f"attendance_{employee.id}_{today}_out.jpg"
                        attendance.face_image_check_out.save(file_name, ContentFile(img_data), save=False)
                    except:
                        pass # Non-critical for checkout in this version
                
                attendance.check_out = current_time
            else:
                return Response({"error": "Invalid action"}, status=400)
                
            attendance.save()
            return Response({
                "status": "success",
                "check_in": attendance.check_in.strftime('%H:%M:%S') if attendance.check_in else None,
                "check_out": attendance.check_out.strftime('%H:%M:%S') if attendance.check_out else None,
                "distance": round(distance, 2)
            })
        except Exception as e:
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=500)
