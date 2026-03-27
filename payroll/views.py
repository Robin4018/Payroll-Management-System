from rest_framework import viewsets, permissions, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from datetime import datetime
from .models import PayrollLedger, SalaryComponent, EmployeeSalaryStructure, PayrollAdjustment
from .serializers import PayrollLedgerSerializer, SalaryComponentSerializer, EmployeeSalaryStructureSerializer, PayrollAdjustmentSerializer
from .utils import generate_payslip, generate_payroll_excel
from django.conf import settings
import os
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image as RLImage
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class SalaryComponentViewSet(ModelViewSet):
    serializer_class = SalaryComponentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return SalaryComponent.objects.filter(tenant=user.employee.tenant)
        
        if hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            # Filter by the first tenant of that type if no employee record is found
            from tenants.models import Tenant
            tenant = Tenant.objects.filter(type=tenant_type).first()
            if tenant:
                return SalaryComponent.objects.filter(tenant=tenant)
            
        return SalaryComponent.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        tenant = None
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        elif hasattr(user, 'profile'):
            from tenants.models import Tenant
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first()
        
        if tenant:
            serializer.save(tenant=tenant)
        else:
            raise ValidationError("Could not determine tenant for this user.")

class EmployeeSalaryStructureViewSet(ModelViewSet):
    queryset = EmployeeSalaryStructure.objects.all()
    serializer_class = EmployeeSalaryStructureSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = EmployeeSalaryStructure.objects.all()
        
        if hasattr(user, 'employee') and user.employee.tenant:
            queryset = queryset.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            queryset = queryset.filter(employee__tenant__type=tenant_type)
        
        emp_id = self.request.query_params.get('employee')
        if emp_id:
            queryset = queryset.filter(employee_id=emp_id)
        return queryset

    @action(detail=False, methods=['post'], url_path='bulk_update')
    def bulk_update_structure(self, request):
        employee_id = request.data.get('employee_id')
        items = request.data.get('items', [])
        
        if not employee_id:
            return Response({"error": "Employee ID required"}, status=400)
            
        from employees.models import Employee
        try:
             # Verify employee exists and belongs to the same tenant if restricted
             if hasattr(request.user, 'employee'):
                 Employee.objects.get(id=employee_id, tenant=request.user.employee.tenant)
             else:
                 Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
             return Response({"error": "Employee not found or unauthorized"}, status=404)

        # Naive approach: clear old structure, add new. 
        # This is safe because we are passing the FULL structure ideally.
        # But wait, frontend sends ONLY what is in the list.
        # If we delete all, we might lose things not in the list if the list is partial?
        # The frontend iterates ALL global components, so it should be a full list.
        # So deleting all for this employee is safe and cleaner than upserting one by one.
        
        EmployeeSalaryStructure.objects.filter(employee_id=employee_id).delete()
        
        new_objects = []
        for item in items:
            amount = item.get('amount', 0)
            # Only save non-zero or important components? 
            # Better to save everything so we know it's 0 explicitly, or just save > 0.
            # Let's save all to be safe.
            new_objects.append(EmployeeSalaryStructure(
                employee_id=employee_id,
                component_id=item.get('component'),
                amount=amount
            ))
            
        EmployeeSalaryStructure.objects.bulk_create(new_objects)
        
        return Response({"message": "Structure updated successfully"})

    @action(detail=False, methods=['post'], url_path='calculate-from-ctc')
    def calculate_from_ctc(self, request):
        employee_id = request.data.get('employee_id')
        ctc_amount = request.data.get('ctc')
        
        if not employee_id or not ctc_amount:
            return Response({"error": "employee_id and ctc are required"}, status=400)
            
        from employees.models import Employee
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
            
        from .structure_service import SalaryStructureService
        service = SalaryStructureService(employee.tenant)
        
        try:
            breakdown = service.structure_salary(employee, ctc_amount)
            return Response(breakdown)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PayrollAdjustmentViewSet(ModelViewSet):
    queryset = PayrollAdjustment.objects.all()
    serializer_class = PayrollAdjustmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.all()
        if hasattr(user, 'employee') and user.employee.tenant:
            qs = qs.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            qs = qs.filter(employee__tenant__type=tenant_type)
        return qs

from .models import SalaryTemplate, SalaryTemplateConfig
from .serializers import SalaryTemplateSerializer

class SalaryTemplateViewSet(ModelViewSet):
    serializer_class = SalaryTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return SalaryTemplate.objects.filter(tenant=user.employee.tenant)
        
        if hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            return SalaryTemplate.objects.filter(tenant__type=tenant_type)
            
        return SalaryTemplate.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        tenant = None
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        elif hasattr(user, 'profile'):
            from tenants.models import Tenant
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first()
        
        if tenant:
            serializer.save(tenant=tenant)
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Could not determine tenant for this user.")



    @action(detail=True, methods=['post'], url_path='assign-to-employee')
    def assign_to_employee(self, request, pk=None):
        template = self.get_object()
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response({"error": "Employee ID required"}, status=400)
            
        from employees.models import Employee
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
            
        # Clear existing structure
        EmployeeSalaryStructure.objects.filter(employee=employee).delete()
        
        # Apply new structure
        configs = template.configs.all()
        new_structures = []
        for config in configs:
            new_structures.append(EmployeeSalaryStructure(
                employee=employee,
                component=config.component,
                amount=config.default_amount
            ))
        
        EmployeeSalaryStructure.objects.bulk_create(new_structures)
        
        return Response({"message": f"Template {template.name} applied to {employee.first_name}"})

    @action(detail=True, methods=['post'], url_path='assign-bulk')
    def assign_bulk(self, request, pk=None):
        """
        Assign a template to multiple employees or all employees in a tenant.
        """
        template = self.get_object()
        employee_ids = request.data.get('employee_ids', [])
        apply_to_all = request.data.get('apply_to_all', False)
        # We rely on the template's tenant to filter employees if apply_to_all is True
        
        from employees.models import Employee
        
        employees = []
        if apply_to_all:
            # target all employees in the template's tenant
            employees = Employee.objects.filter(tenant=template.tenant)
        elif employee_ids:
            employees = Employee.objects.filter(id__in=employee_ids, tenant=template.tenant)
            
        if not employees:
            return Response({"error": "No valid employees selected"}, status=400)
            
        # Get Template Configs
        configs = template.configs.all()
        if not configs.exists():
            return Response({"error": "Template has no components configured"}, status=400)

        # 1. Delete existing structures for these employees
        # Use bulk delete
        EmployeeSalaryStructure.objects.filter(employee__in=employees).delete()
        
        # 2. Prepare new structures
        new_structures = []
        for emp in employees:
            for config in configs:
                new_structures.append(EmployeeSalaryStructure(
                    employee=emp,
                    component=config.component,
                    amount=config.default_amount
                ))
        
        # 3. Bulk Create
        EmployeeSalaryStructure.objects.bulk_create(new_structures)
        
        return Response({"message": f"Template '{template.name}' applied to {len(employees)} employees."})

from .serializers import SalaryTemplateConfigSerializer

class SalaryTemplateConfigViewSet(ModelViewSet):
    queryset = SalaryTemplateConfig.objects.all()
    serializer_class = SalaryTemplateConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

class PayrollLedgerViewSet(ModelViewSet):
    queryset = PayrollLedger.objects.all()
    serializer_class = PayrollLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = self.queryset.select_related('employee', 'employee__bank_details')
        
        # 1. Tenant Isolation
        if hasattr(user, 'employee') and user.employee.tenant:
            qs = qs.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            qs = qs.filter(employee__tenant__type=tenant_type)

        # 2. Staff View Restriction
        is_admin = user.is_superuser or user.is_staff or (hasattr(user, 'employee') and user.groups.filter(name='Admin').exists())
        
        if not is_admin and hasattr(user, 'employee'):
            qs = qs.filter(employee=user.employee)
        
        # 3. Query Param Filtering
        month = self.request.query_params.get('month')
        status_param = self.request.query_params.get('status')
        if month:
            qs = qs.filter(month=month)
        if status_param:
            qs = qs.filter(status=status_param)
            
        return qs

    @action(detail=False, methods=['get'], url_path='my-payslips')
    def my_payslips(self, request):
        user = request.user
        if hasattr(user, 'employee'):
            # Return payslips ordered by month descending
            queryset = self.queryset.filter(employee=user.employee).order_by('-month')
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])


    @action(detail=False, methods=["post"], url_path="run")
    def run_payroll(self, request):
        tenant_id = request.data.get("tenant_id") # Optional if using request.user.tenant
        month_str = request.data.get("month")
        employee_ids = request.data.get("employee_ids", []) # List[int] or "ALL" or "DEPT:x"
        
        if not month_str:
            return Response({"error": "Month is required (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            month = datetime.strptime(month_str, "%Y-%m-%d").date().replace(day=1)
        except ValueError:
             return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        # Tenant handling
        user = request.user
        tenant = None
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        elif hasattr(user, 'profile'):
            from tenants.models import Tenant
            org_type = getattr(user.profile, 'organization_type', 'COMPANY')
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first()
        
        if not tenant:
            from tenants.models import Tenant
            tenant = Tenant.objects.first()

        from .services import PayrollCalculator
        calculator = PayrollCalculator(tenant)
        
        # Determine employee list
        target_employees = None
        if employee_ids and isinstance(employee_ids, list) and len(employee_ids) > 0:
            target_employees = employee_ids
        
        try:
            results = calculator.run_payroll_for_tenant(month, employee_list=target_employees)
            
            # Trigger Notification to Admin
            from notifications.utils import send_notification
            send_notification(
                user=request.user,
                title="Payroll Completed",
                message=f"Payroll for {month_str} has been successfully calculated for {len(results)} employees.",
                notif_type='PAYROLL'
            )
            
            return Response({
                "task_id": "sync-completed"
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"], url_path="export-excel")
    def export_excel(self, request):
        """
        Exports payroll data to Excel.
        """
        from .utils import generate_payroll_excel
        from datetime import datetime
        
        month_str = request.data.get('month')
        tenant_id = request.data.get('tenant_id')
        ledger_ids = request.data.get('ledger_ids', [])

        if not month_str:
            return Response({"error": "Month is required"}, status=400)

        # Resolve tenant_id if not provided
        if not tenant_id:
            if hasattr(request.user, 'employee'):
                tenant_id = request.user.employee.tenant_id
            elif hasattr(request.user, 'profile'):
                from tenants.models import Tenant
                tenant = Tenant.objects.first() # Default for now
                if tenant: tenant_id = tenant.id

        month_date = datetime.strptime(month_str, "%Y-%m-%d").date().replace(day=1)
        
        if ledger_ids:
            ledgers = self.queryset.filter(id__in=ledger_ids)
        else:
            ledgers = self.queryset.filter(employee__tenant_id=tenant_id, month=month_date)
        
        if not ledgers.exists():
            return Response({"error": "No records found to export."}, status=404)
            
        file_path = generate_payroll_excel(ledgers)
        return Response({"file_url": file_path})

    @action(detail=True, methods=["get"])
    def payslip(self, request, pk=None):
        payroll = self.get_object()
        file_path = generate_payslip(payroll)
        return Response({"payslip": file_path})

    @action(detail=True, methods=["post"], url_path='email-payslip')
    def email_payslip(self, request, pk=None):
        """
        Sends the payslip PDF via email to the employee.
        """
        payroll = self.get_object()
        file_path = generate_payslip(payroll)
        
        import os
        from django.conf import settings
        from django.core.mail import EmailMessage
        
        abs_path = os.path.join(settings.BASE_DIR, file_path.lstrip('/'))
        
        if not os.path.exists(abs_path):
             return Response({"error": "PDF not found"}, status=404)

        subject = f"Payslip for {payroll.month.strftime('%B %Y')}"
        body = f"Dear {payroll.employee.first_name},\n\nPlease find attached your payslip for {payroll.month.strftime('%B %Y')}.\n\nRegards,\nCollege Admin"
        
        email = EmailMessage(
            subject, body, settings.EMAIL_HOST_USER, [payroll.employee.email]
        )
        email.attach_file(abs_path)
        
        try:
            email.send(fail_silently=False)
            return Response({"message": "Email sent successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"], url_path='bulk-email')
    def bulk_email(self, request):
        ledger_ids = request.data.get('ledger_ids', [])
        if not ledger_ids:
            return Response({"error": "No records selected"}, status=400)
            
        ledgers = PayrollLedger.objects.filter(id__in=ledger_ids)
        success_count = 0
        
        from .utils import generate_payslip
        from django.core.mail import EmailMessage
        from django.conf import settings
        import os

        for ledger in ledgers:
            try:
                file_path = generate_payslip(ledger)
                abs_path = os.path.join(settings.BASE_DIR, file_path.lstrip('/'))
                
                subject = f"Payslip for {ledger.month.strftime('%B %Y')}"
                body = f"Dear {ledger.employee.first_name},\n\nPlease find attached your payslip for {ledger.month.strftime('%B %Y')}."
                
                email = EmailMessage(subject, body, settings.EMAIL_HOST_USER, [ledger.employee.email])
                email.attach_file(abs_path)
                email.send()
                success_count += 1
            except:
                continue
                
        return Response({"message": f"Dispatched {success_count} emails successfully."})

    @action(detail=False, methods=["post"], url_path="generate-bank-file")
    def generate_bank_file(self, request):
        """
        Input: { "tenant_id": 1, "month": "2023-10-01" }
        """
        from .utils import generate_bank_transfer_file
        from datetime import datetime
        
        tenant_id = request.data.get('tenant_id')
        month_str = request.data.get('month')
        ledger_ids = request.data.get('ledger_ids', [])
        
        # Robust tenant resolution
        if not tenant_id:
            if hasattr(request.user, 'employee') and request.user.employee.tenant_id:
                tenant_id = request.user.employee.tenant_id
            elif hasattr(request.user, 'profile'):
                # Try to get tenant from somewhere else if profile mentions it, 
                # but for simplicity we'll use first tenant as a fallback for admins
                from tenants.models import Tenant
                tenant = Tenant.objects.first()
                if tenant: tenant_id = tenant.id
            elif request.user.is_superuser:
                from tenants.models import Tenant
                tenant = Tenant.objects.filter(type='EDUCATION').first() or Tenant.objects.first()
                if tenant: tenant_id = tenant.id

        if not month_str:
            return Response({"error": "Month required"}, status=400)

        month_date = datetime.strptime(month_str, "%Y-%m-%d").date().replace(day=1)
        
        if ledger_ids:
            ledgers = self.queryset.filter(id__in=ledger_ids)
        else:
            # Get only records for the month. 
            # Usually only APPROVED or PAID ones should go in bank file, 
            # but we'll include everything filtered by tenant.
            ledgers = self.queryset.filter(employee__tenant_id=tenant_id, month=month_date)
        
        if not ledgers.exists():
            return Response({"error": "No records found for the selected period."}, status=404)
            
        file_path = generate_bank_transfer_file(ledgers)
        return Response({"file_url": file_path})

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        ledger = self.get_object()
        if ledger.status != PayrollLedger.Status.DRAFT:
            return Response({"error": "Can only finalize draft records"}, status=400)
        ledger.status = PayrollLedger.Status.LOCKED
        ledger.save()

        # Notify Employee
        if ledger.employee.user:
            from notifications.utils import send_notification
            send_notification(
                user=ledger.employee.user,
                title="Payroll Finalized",
                message=f"Your payroll for {ledger.month.strftime('%B %Y')} has been finalized. You can now view your payslip.",
                notif_type='PAYROLL'
            )
        return Response({"status": "Finalized"})

    @action(detail=False, methods=['post'], url_path='bulk-approve')
    def bulk_approve(self, request):
        ledger_ids = request.data.get('ledger_ids', [])
        ledgers = self.queryset.filter(id__in=ledger_ids, status=PayrollLedger.Status.DRAFT)
        
        from notifications.utils import send_notification
        month_str = ""
        for l in ledgers:
            month_str = l.month.strftime('%B %Y')
            l.status = PayrollLedger.Status.LOCKED
            l.save()
            # Notify each employee
            if l.employee.user:
                send_notification(
                    user=l.employee.user,
                    title="Payroll Finalized",
                    message=f"Your payroll for {month_str} has been finalized. View your payslip in the portal.",
                    notif_type='PAYROLL'
                )

        # Notify Admins/Principal
        from notifications.utils import notify_admins
        if ledgers.exists(): # Only notify if there were ledgers to finalize
            # month_str will be set from the last ledger in the loop, or remain empty if no ledgers
            # If ledgers is not empty, month_str will have a value.
            notify_admins(
                title="Payroll Finalized & Ready",
                message=f"Payroll for {month_str} has been finalized across {len(ledgers)} employees and is ready for bank disbursement authorization.",
                notif_type='PAYROLL'
            )

        return Response({"status": f"Bulk finalized {len(ledgers)} records"})

    @action(detail=True, methods=['post'], url_path='mark_paid')
    def mark_paid(self, request, pk=None):
        ledger = self.get_object()
        utr = request.data.get('utr_number')
        if not utr:
            return Response({"error": "UTR number required"}, status=400)
        ledger.status = PayrollLedger.Status.PAID
        ledger.utr_number = utr
        ledger.payment_date = datetime.now().date()
        ledger.save()
        return Response({"status": "Disbursed"})

    @action(detail=False, methods=['post'], url_path='bulk-remit')
    def bulk_remit(self, request):
        ledger_ids = request.data.get('ledger_ids', [])
        utr = request.data.get('utr_number')
        if not utr:
            return Response({"error": "UTR number required"}, status=400)
        ledgers = self.queryset.filter(id__in=ledger_ids, status=PayrollLedger.Status.LOCKED)
        count = ledgers.count()
        ledgers.update(
            status=PayrollLedger.Status.PAID,
            utr_number=utr,
            payment_date=datetime.now().date()
        )
        # Notify Admins/Principal
        from notifications.utils import notify_admins
        notify_admins(
            title="Disbursement Request Sent",
            message=f"Payroll disbursement for {count} employees has been initiated. Bank transfer files are ready for review.",
            notif_type='PAYROLL'
        )
        return Response({"status": f"Bulk disbursed {count} records"})


    @action(detail=False, methods=['get'], url_path='consolidated-report')
    def consolidated_report(self, request):
        """
        Comprehensive reporting engine for preview and download.
        ?type=monthly|dept|deduction|tax|cost|attendance
        &month=2024-02
        &export_format=excel|pdf (optional)
        """
        from datetime import datetime
        report_type = request.query_params.get('type', 'monthly')
        month_str = request.query_params.get('month')
        fmt = request.query_params.get('export_format') # Use export_format to avoid DRF 'format' collision
        
        if not month_str:
            return Response({"error": "Month parameter required"}, status=400)
            
        try:
            # Handle YYYY-MM
            if len(month_str) == 7:
                month_date = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
            else:
                month_date = datetime.strptime(month_str, "%Y-%m-%d").date().replace(day=1)
        except:
            return Response({"error": "Invalid date format"}, status=400)

        # Tenant filtering
        tenant_id = None
        if hasattr(request.user, 'staff_profile'):
            tenant_id = request.user.staff_profile.tenant_id
        elif hasattr(request.user, 'employee'):
            tenant_id = request.user.employee.tenant_id
            
        ledgers = self.queryset.filter(month=month_date)
        if tenant_id:
            ledgers = ledgers.filter(employee__tenant_id=tenant_id)
        
        # Master Register Special Handling (Multi-sheet Excel)
        if report_type == 'master' and fmt == 'excel':
            import os
            from django.conf import settings
            fname = f"master_register_{month_date}.xlsx"
            fpath = os.path.join(settings.BASE_DIR, 'media', 'reports', fname)
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            
            with pd.ExcelWriter(fpath, engine='openpyxl') as writer:
                # All sub-reports
                sub_types = ['monthly', 'dept', 'deduction', 'tax', 'cost', 'attendance']
                for st in sub_types:
                    sub_data = self._get_report_data(st, ledgers, month_date)
                    if sub_data:
                        pd.DataFrame(sub_data).to_excel(writer, sheet_name=st.title(), index=False)
                    else:
                        pd.DataFrame([{"Message": "No data"}]).to_excel(writer, sheet_name=st.title(), index=False)
            
            return Response({"file_url": f"/media/reports/{fname}"})

        data = self._get_report_data(report_type, ledgers, month_date)
        
        if not fmt:
            return Response(data)
            
        # Generate Files
        if fmt == 'excel':
            import os
            import pandas as pd
            from django.conf import settings
            
            # Use the specific data generated for this report type
            if data:
                df = pd.DataFrame(data)
                # Ensure headers are professional
                df.columns = [c.replace('_', ' ').replace('amount', '(Rs)').upper() for c in df.columns]
                
                fname = f"report_{report_type}_{month_date}.xlsx"
                fpath = os.path.join(settings.BASE_DIR, 'media', 'reports', fname)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                
                df.to_excel(fpath, index=False)
                return Response({"file_url": f"/media/reports/{fname}"})
            else:
                return Response({"error": "No data available for export"}, status=404)
            
        elif fmt == 'pdf':
            file_path = self._generate_report_pdf(report_type, data, month_date)
            return Response({"file_url": file_path})
            
        return Response(data)

    def _generate_report_pdf(self, title, data, month_date):
        """
        High-fidelity institutional report generator with branding, headers, and footers.
        """
        file_name = f"report_{title}_{month_date}.pdf"
        save_path = os.path.join(settings.BASE_DIR, 'media', 'reports', file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Paths for signature and seal
        assets_dir = os.path.join(settings.BASE_DIR, 'media', 'assets', 'branding')
        sign_img_path = os.path.join(assets_dir, 'payslip_signature.png')

        doc = SimpleDocTemplate(save_path, pagesize=landscape(A4),
                                rightMargin=40, leftMargin=40, 
                                topMargin=30, bottomMargin=60)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom Colors & Styles
        maroon = colors.HexColor('#800000')
        navy = colors.HexColor('#1a237e')
        
        style_org_top = ParagraphStyle('OrgTop', parent=styles['Normal'], alignment=1, fontSize=9, textColor=colors.black, fontName='Helvetica-Bold')
        style_org_main = ParagraphStyle('OrgMain', parent=styles['Normal'], alignment=1, fontSize=22, textColor=maroon, fontName='Helvetica-Bold', leading=26)
        style_org_sub = ParagraphStyle('OrgSub', parent=styles['Normal'], alignment=1, fontSize=9, textColor=colors.black, fontName='Helvetica')
        style_officials = ParagraphStyle('Officials', parent=styles['Normal'], alignment=1, fontSize=11, textColor=maroon, fontName='Helvetica-Bold')
        style_roles = ParagraphStyle('Roles', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.black, fontName='Helvetica')
        
        # Table Cell Styles
        style_cell = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=7.5, leading=9, alignment=0) 
        style_cell_center = ParagraphStyle('TableCellCenter', parent=styles['Normal'], fontSize=7.5, leading=9, alignment=1)
        style_header = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=8, textColor=colors.whitesmoke, fontName='Helvetica-Bold', alignment=1)

        # 1. Institutional Header
        elements.append(Paragraph("CHURCH OF SOUTH INDIA TRUST ASSOCIATION - COIMBATORE DIOCESE", style_org_top))
        elements.append(Spacer(1, 0.05*inch))
        elements.append(Paragraph("BISHOP APPASAMY COLLEGE OF ARTS & SCIENCE", style_org_main))
        elements.append(Paragraph("(Affiliated to Bharathiar University, Approved by AICTE - New Delhi)", style_org_sub))
        elements.append(Paragraph("(Accredited by NAAC, ISO 9001 : 2015 Certified)", style_org_sub))
        
        # Officials Block (Landscape Optimized Widths)
        elements.append(Spacer(1, 0.2*inch))
        official_lower = [
            [
                Paragraph("Rt.Rev. TIMOTHY RAVINDER", style_officials),
                Paragraph("Rev. L. DAVID BARNABAS", style_officials),
                Paragraph("Dr. Mrs. JEMIMAH WINSTON", style_officials)
            ],
            [
                Paragraph("Chairman & Bishop in Coimbatore", style_roles),
                Paragraph("Secretary", style_roles),
                Paragraph("Principal", style_roles)
            ]
        ]
        t_lower = Table(official_lower, colWidths=[3.3*inch, 3.3*inch, 3.3*inch])
        elements.append(t_lower)
        
        # Decorative Lines
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=navy, spaceBefore=1, spaceAfter=1))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceBefore=1, spaceAfter=15))

        # 2. Report Title
        report_title_style = ParagraphStyle('ReportTitle', parent=styles['Title'], alignment=1, fontSize=16, textColor=navy, fontName='Helvetica-Bold', spaceAfter=10)
        elements.append(Paragraph(f"{title.replace('_', ' ').upper()} REPORT", report_title_style))
        elements.append(Paragraph(f"Financial Period: {month_date.strftime('%B %Y')}", ParagraphStyle('Period', parent=styles['Normal'], alignment=1, fontSize=11, spaceAfter=20)))
        
        # 3. Data Table
        if data:
            headers = [h.replace('_', ' ').upper() for h in data[0].keys()]
            table_data = [[Paragraph(h, style_header) for h in headers]]
            
            for row in data:
                row_data = []
                for h in data[0].keys():
                    val = str(row.get(h, ''))
                    h_upper = h.upper()
                    # Use left-align for text-heavy columns, center-align for numbers/codes
                    if any(x in h_upper for x in ['EMPLOYEE', 'DESIGNATION', 'DEPARTMENT', 'NAME']):
                        row_data.append(Paragraph(val, style_cell))
                    else:
                        row_data.append(Paragraph(val, style_cell_center))
                table_data.append(row_data)
            
            # Intelligent Width Calculation
            num_cols = len(headers)
            avail_width = 10.5 * inch
            weights = []
            for h in headers:
                h_upper = h.upper()
                if 'EMPLOYEE' in h_upper or 'DESIGNATION' in h_upper or 'NAME' in h_upper:
                    weights.append(2.2) # More width for text
                elif 'DEPARTMENT' in h_upper:
                    weights.append(1.8)
                elif 'PAN' in h_upper or 'CODE' in h_upper or 'STATUS' in h_upper:
                    weights.append(1.2)
                else:
                    weights.append(1.0) # Standard width for numbers
            
            total_weight = sum(weights)
            col_widths = [(w / total_weight) * avail_width for w in weights] if num_cols > 0 else None
            
            t = Table(table_data, repeatRows=1, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), navy),
                # TEXTCOLOR and FONT are handled by Paragraph style
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("No data available for this selection.", styles['Normal']))

        # 4. Signature Block
        elements.append(Spacer(1, 0.4*inch))
        if os.path.exists(sign_img_path):
            sign_img = RLImage(sign_img_path, width=2.4*inch, height=1.2*inch)
            sign_img.hAlign = 'LEFT'
            elements.append(sign_img)

        # 5. Footer Definition
        def add_footer(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(navy)
            canvas.line(40, 50, landscape(A4)[0]-40, 50)
            canvas.setFont('Helvetica', 7.5)
            footer_text = "129, Race Course, Coimbatore - 641 018, TN. | Ph: 0422 - 2221840 | Email: csibacas@gmail.com | www.csibacas.org"
            canvas.drawCentredString(landscape(A4)[0]/2, 38, footer_text)
            canvas.drawCentredString(landscape(A4)[0]/2, 28, "Accredited by NAAC, ISO 9001:2015 Certified | Recognized by UGC under Section 2(f) and 12(B)")
            canvas.restoreState()

        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        return f"/media/reports/{file_name}"

    def _get_report_data(self, report_type, ledgers, month_date):
        data = []
        try:
            if report_type == 'monthly':
                for l in ledgers:
                    data.append({
                        "Employee": f"{l.employee.first_name} {l.employee.last_name}",
                        "Code": l.employee.employee_code,
                        "Earnings": float(l.total_earnings),
                        "Deductions": float(l.total_deductions),
                        "Net Pay": float(l.net_pay),
                        "Status": l.status
                    })
            elif report_type == 'dept':
                depts = {}
                for l in ledgers:
                    d_name = l.employee.department.name if l.employee.department else 'Unassigned'
                    if d_name not in depts:
                        depts[d_name] = {'count': 0, 'total_payout': 0}
                    depts[d_name]['count'] += 1
                    depts[d_name]['total_payout'] += float(l.net_pay)
                for k, v in depts.items():
                    data.append({"Department": k, "Employee Count": v['count'], "Total Payout": v['total_payout']})
            elif report_type == 'deduction':
                for l in ledgers:
                    breakdown = l.calculations_breakdown or {}
                    lop_item = breakdown.get('lop', 0)
                    lop_val = 0
                    if isinstance(lop_item, dict):
                        lop_val = lop_item.get('amount', 0)
                    else:
                        lop_val = lop_item
                        
                    data.append({
                        "Employee": f"{l.employee.first_name}",
                        "Total Deduction": float(l.total_deductions),
                        "PF": float(l.pf_amount),
                        "ESI": float(l.esi_amount),
                        "Professional Tax": float(l.pt_amount),
                        "LOP": float(lop_val)
                    })
            elif report_type == 'tax':
                for l in ledgers:
                    bank = getattr(l.employee, 'bank_details', None)
                    data.append({
                        "Employee": f"{l.employee.first_name} {l.employee.last_name}",
                        "Designation": l.employee.designation or "-",
                        "PAN": bank.pan_number if bank and bank.pan_number else "N/A",
                        "Gross Salary": float(l.total_earnings),
                        "TDS Deducted": float(l.tds_amount),
                        "Net Payout": float(l.net_pay)
                    })
            elif report_type == 'cost':
                for l in ledgers:
                    gross = float(l.total_earnings)
                    # Institutional breakdown
                    data.append({
                        "Employee": f"{l.employee.first_name} {l.employee.last_name}",
                        "Designation": l.employee.designation or "-",
                        "Gross Pay": gross,
                        "Employer PF (12%)": round(gross * 0.12, 2), 
                        "Employer ESI (3.25%)": round(gross * 0.0325, 2),
                        "Gratuity (4.81%)": round(gross * 0.0481, 2),
                        "Total CTC (Monthly)": round(gross * 1.2006, 2)
                    })
            elif report_type == 'attendance':
                from attendance.models import Attendance
                import calendar
                _, num_days = calendar.monthrange(month_date.year, month_date.month)
                start = month_date
                end = month_date.replace(day=num_days)
                for l in ledgers:
                    # Filter attendance records for this month
                    attendance_qs = Attendance.objects.filter(employee=l.employee, date__range=[start, end])
                    present = attendance_qs.filter(status='PRESENT').count()
                    absent = attendance_qs.filter(status='ABSENT').count()
                    on_leave = attendance_qs.filter(status='LEAVE').count()
                    
                    data.append({
                        "Employee": f"{l.employee.first_name} {l.employee.last_name}",
                        "Total Days": num_days,
                        "Days Present": present,
                        "Days Absent": absent,
                        "On Leave": on_leave,
                        "Net Payout": float(l.net_pay)
                    })
        except Exception as e:
            print(f"Error in _get_report_data for {report_type}: {str(e)}")
        return data

from .models import Loan
from .serializers import LoanSerializer

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        loan = serializer.save()
        # Notify Admins
        from notifications.utils import notify_admins
        notify_admins(
            title="New Loan Request",
            message=f"{loan.employee.first_name} {loan.employee.last_name} has requested a loan of INR {loan.amount}.",
            notif_type='GENERAL'
        )

    def get_queryset(self):
        user = self.request.user
        qs = Loan.objects.all().select_related('employee')
        
        # 1. Tenant Isolation
        if hasattr(user, 'employee') and user.employee.tenant:
            qs = qs.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            qs = qs.filter(employee__tenant__type=tenant_type)

        # 2. Staff View Restriction
        is_admin = user.is_superuser or user.is_staff or (hasattr(user, 'employee') and user.groups.filter(name='Admin').exists())
        
        if not is_admin and hasattr(user, 'employee'):
            return qs.filter(employee=user.employee)
            
        return qs

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        loan = self.get_object()
        if loan.status != Loan.Status.PENDING:
            return Response({"error": "Only pending loans can be approved"}, status=400)
            
        loan.status = Loan.Status.ACTIVE
        loan.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
        loan.start_date = request.data.get('start_date') 
        # If start_date not provided, could default to next month.
        loan.save()
        return Response({"status": "Loan Approved"})

from .models import Reimbursement
from .serializers import ReimbursementSerializer

class ReimbursementViewSet(viewsets.ModelViewSet):
    queryset = Reimbursement.objects.all()
    serializer_class = ReimbursementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        r = serializer.save()
        # Notify Admins
        from notifications.utils import notify_admins
        notify_admins(
            title="New Reimbursement Claim",
            message=f"{r.employee.first_name} {r.employee.last_name} has submitted a claim for INR {r.amount} ({r.title}).",
            notif_type='GENERAL'
        )

    def get_queryset(self):
        user = self.request.user
        qs = Reimbursement.objects.all().select_related('employee')
        
        # 1. Tenant Isolation
        if hasattr(user, 'employee') and user.employee.tenant:
            qs = qs.filter(employee__tenant=user.employee.tenant)
        elif hasattr(user, 'profile'):
            tenant_type = 'CORPORATE' if user.profile.organization_type == 'COMPANY' else 'EDUCATION'
            qs = qs.filter(employee__tenant__type=tenant_type)

        # 2. Staff View Restriction
        is_admin = user.is_superuser or user.is_staff or (hasattr(user, 'employee') and user.groups.filter(name='Admin').exists())
        
        if not is_admin and hasattr(user, 'employee'):
            return qs.filter(employee=user.employee)
            
        return qs

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        r = self.get_object()
        if r.status != Reimbursement.Status.PENDING:
             return Response({"error": "Can only approve pending claims"}, status=400)
        
        # Phase 1: Admin Approval -> Locks and Notifies Principal
        r.status = Reimbursement.Status.LOCKED
        r.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
        r.save()

        # Notify Principal/Admins
        from notifications.utils import notify_admins
        notify_admins(
            title="Reimbursement Over-Approval Required",
            message=f"Admin has pre-approved a claim of INR {r.amount} for {r.employee.first_name}. Final Principal approval is now required.",
            notif_type='GENERAL'
        )
        return Response({"status": "Admin Approved (Waiting for Principal)"})

    @action(detail=True, methods=['post'], url_path='principal_approve')
    def principal_approve(self, request, pk=None):
        r = self.get_object()
        if r.status != Reimbursement.Status.LOCKED:
             return Response({"error": "Can only finalize claims already approved by Admin"}, status=400)
        
        # Phase 2: Principal Approval -> Final Approved
        r.status = Reimbursement.Status.APPROVED
        r.save()

        # Final Notification to Employee
        if r.employee.user:
            from notifications.utils import send_notification
            send_notification(
                user=r.employee.user,
                title="Reimbursement Finalized",
                message=f"Your claim for '{r.title}' has received final approval from the Principal.",
                notif_type='GENERAL'
            )
        return Response({"status": "Final Approved (Principal)"})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        r = self.get_object()
        if r.status not in [Reimbursement.Status.PENDING, Reimbursement.Status.LOCKED]:
             return Response({"error": "Cannot reject already processed claims"}, status=400)
        r.status = Reimbursement.Status.REJECTED
        r.save()
        return Response({"status": "Rejected"})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        tenant = None
        if hasattr(user, 'employee') and user.employee.tenant:
            tenant = user.employee.tenant
        elif hasattr(user, 'profile'):
            from tenants.models import Tenant
            org_type = getattr(user.profile, 'organization_type', 'COMPANY')
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            tenant = Tenant.objects.filter(type=tenant_type).first()
        
        if not tenant:
            return Response({"pending_amount": 0, "approved_amount": 0, "settled_amount": 0})

        from django.db.models import Sum
        pending = Reimbursement.objects.filter(employee__tenant=tenant, status=Reimbursement.Status.PENDING).aggregate(Sum('amount'))['amount__sum'] or 0
        approved = Reimbursement.objects.filter(employee__tenant=tenant, status=Reimbursement.Status.APPROVED).aggregate(Sum('amount'))['amount__sum'] or 0
        settled = Reimbursement.objects.filter(employee__tenant=tenant, status=Reimbursement.Status.PAID).aggregate(Sum('amount'))['amount__sum'] or 0

        return Response({
            "pending_amount": float(pending),
            "approved_amount": float(approved),
            "settled_amount": float(settled)
        })

class BankPaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_tenant(self, request):
        user = request.user
        if hasattr(user, 'employee') and user.employee.tenant:
            return user.employee.tenant
        if hasattr(user, 'profile'):
            from tenants.models import Tenant
            org_type = getattr(user.profile, 'organization_type', 'COMPANY')
            tenant_type = 'CORPORATE' if org_type == 'COMPANY' else 'EDUCATION'
            return Tenant.objects.filter(type=tenant_type).first()
        return None

    def list(self, request):
        tenant = self._get_tenant(request)
        if not tenant:
            return Response([])

        from django.db.models import Sum, Count, Q
        from .models import PayrollLedger
        batches = PayrollLedger.objects.filter(employee__tenant=tenant).values('month').annotate(
            amount=Sum('net_pay'),
            beneficiary_count=Count('id'),
            processed_count=Count('id', filter=Q(status=PayrollLedger.Status.PAID)),
        ).order_by('-month')

        results = []
        for b in batches:
            status = 'PENDING'
            if b['processed_count'] == b['beneficiary_count'] and b['beneficiary_count'] > 0:
                status = 'PAID'
            elif b['processed_count'] > 0:
                status = 'PARTIAL'
            
            results.append({
                "id": b['month'].strftime('%Y%m'),
                "cycle_name": b['month'].strftime('%B %Y'),
                "payment_date": b['month'].strftime('%Y-%m-01'),
                "beneficiary_count": b['beneficiary_count'],
                "amount": float(b['amount']),
                "payment_method": "Bank Transfer",
                "status": status
            })
        
        return Response(results)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        tenant = self._get_tenant(request)
        if not tenant:
            return Response({"total_disbursed": 0, "unsettled_batches": 0})

        from django.db import models
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        import datetime
        from .models import PayrollLedger

        # 1. Total Disbursed (Last 12M)
        twelve_months_ago = timezone.now().date() - datetime.timedelta(days=365)
        total_disbursed = PayrollLedger.objects.filter(
            employee__tenant=tenant,
            status=PayrollLedger.Status.PAID,
            payment_date__gte=twelve_months_ago
        ).aggregate(Sum('net_pay'))['net_pay__sum'] or 0

        # 2. Unsettled Batches (Months that have LOCKED/DRAFT records)
        unsettled_months = PayrollLedger.objects.filter(
            employee__tenant=tenant
        ).exclude(status=PayrollLedger.Status.PAID).values('month').distinct().count()

        return Response({
            "total_disbursed": float(total_disbursed),
            "unsettled_batches": unsettled_months,
            "compliance_status": "SUCCESS"
        })
