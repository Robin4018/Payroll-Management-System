from rest_framework import viewsets, permissions, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime
from .models import PayrollLedger, SalaryComponent, EmployeeSalaryStructure, PayrollAdjustment
from .serializers import PayrollLedgerSerializer, SalaryComponentSerializer, EmployeeSalaryStructureSerializer, PayrollAdjustmentSerializer
from .utils import generate_payslip

class SalaryComponentViewSet(ModelViewSet):
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer

class EmployeeSalaryStructureViewSet(ModelViewSet):
    queryset = EmployeeSalaryStructure.objects.all()
    serializer_class = EmployeeSalaryStructureSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
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
             # Verify employee exists
             Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
             return Response({"error": "Employee not found"}, status=404)

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

from .models import SalaryTemplate, SalaryTemplateConfig
from .serializers import SalaryTemplateSerializer

class SalaryTemplateViewSet(ModelViewSet):
    queryset = SalaryTemplate.objects.all()
    serializer_class = SalaryTemplateSerializer



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
        if hasattr(user, 'employee'):
            return self.queryset.filter(employee=user.employee)
        return self.queryset

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
        # Assuming single tenant context from user for now, or passed ID.
        if hasattr(request.user, 'employee'):
             tenant = request.user.employee.tenant
        elif hasattr(request.user, 'profile'):
             # Logic to get tenant from profile?
             # For demo, let's assume first tenant or explicit logic
             from tenants.models import Tenant
             tenant = Tenant.objects.first() 
        else:
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
        Input: { "tenant_id": 1, "month": "2023-10-01" }
        """
        from .utils import generate_payroll_excel
        from datetime import datetime
        
        tenant_id = request.data.get('tenant_id')
        month_str = request.data.get('month')
        
        if not tenant_id or not month_str:
            return Response({"error": "tenant_id and month required"}, status=400)

        month_date = datetime.strptime(month_str, "%Y-%m-%d").date()
        ledgers = self.queryset.filter(employee__tenant_id=tenant_id, month=month_date)
        
        if not ledgers.exists():
            return Response({"error": "No payroll records found"}, status=404)
            
        file_path = generate_payroll_excel(ledgers)
        return Response({"file_url": file_path})

    @action(detail=True, methods=["get"])
    def payslip(self, request, pk=None):
        payroll = self.get_object()
        file_path = generate_payslip(payroll)
        return Response({"payslip": file_path})

    @action(detail=True, methods=["post"])
    def email_payslip(self, request, pk=None):
        """
        Sends the payslip PDF via email to the employee.
        """
        payroll = self.get_object()
        file_path = generate_payslip(payroll) # Returns relative path /media/...
        
        # Resolve absolute path for attachment
        import os
        from django.conf import settings
        from django.core.mail import EmailMessage
        
        abs_path = os.path.join(settings.BASE_DIR, file_path.lstrip('/'))
        
        if not os.path.exists(abs_path):
             return Response({"error": "PDF not found"}, status=404)

        subject = f"Payslip for {payroll.month.strftime('%B %Y')}"
        body = f"Dear {payroll.employee.first_name},\n\nPlease find attached your payslip for {payroll.month.strftime('%B %Y')}.\n\nRegards,\nCollege Admin"
        
        email = EmailMessage(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [payroll.employee.email],
        )
        email.attach_file(abs_path)
        
        try:
            email.send(fail_silently=False)
            return Response({"message": "Email sent successfully"})
        except Exception as e:
            # We fail silently here to not crash the UI if SMTP isn't set up, 
            # but allow returning 'success' for the demo unless it's critical.
            # Actually, let's return error so user knows.
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"], url_path="generate-bank-file")
    def generate_bank_file(self, request):
        """
        Input: { "tenant_id": 1, "month": "2023-10-01" }
        """
        from .utils import generate_bank_transfer_file
        from datetime import datetime
        
        tenant_id = request.data.get('tenant_id')
        month_str = request.data.get('month')
        
        if not tenant_id or not month_str:
            return Response({"error": "tenant_id and month required"}, status=400)

        month_date = datetime.strptime(month_str, "%Y-%m-%d").date()
        # Get only PAID or APPROVED records ideally, but here we take all for the month
        ledgers = self.queryset.filter(employee__tenant_id=tenant_id, month=month_date)
        
        if not ledgers.exists():
            return Response({"error": "No records found"}, status=404)
            
        file_path = generate_bank_transfer_file(ledgers)
        return Response({"file_url": file_path})

class ReportViewSet(viewsets.ViewSet):
    """
    Unified Endpoint for Payroll Reports
    Query Params: type (monthly, dept, deduction, tax, cost, attendance), month (YYYY-MM)
    """
    def list(self, request):
        try:
            report_type = request.query_params.get('type')
            month_str = request.query_params.get('month')
            
            # Determine Tenant
            tenant_id = None
            if hasattr(request.user, 'employee'):
                tenant_id = request.user.employee.tenant_id
            else:
                from tenants.models import Tenant
                first_tenant = Tenant.objects.first()
                if first_tenant:
                    tenant_id = first_tenant.id

            if not report_type or not month_str:
                return Response({"error": "type and month required"}, status=400)
                
            from datetime import datetime
            try:
                month_date = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
            except ValueError:
                return Response({"error": "Invalid month format (YYYY-MM)"}, status=400)
            
            # Base Query
            if tenant_id:
                ledgers = PayrollLedger.objects.filter(employee__tenant_id=tenant_id, month=month_date)
            else:
                ledgers = PayrollLedger.objects.filter(month=month_date) # Fallback
            
            data = []
            
            if report_type == 'monthly':
                # Summary of all employees
                for l in ledgers:
                    data.append({
                        "Employee": f"{l.employee.first_name} {l.employee.last_name}",
                        "Code": l.employee.employee_code,
                        "Earnings": l.total_earnings,
                        "Deductions": l.total_deductions,
                        "Net Pay": l.net_pay,
                        "Status": l.status
                    })
                    
            elif report_type == 'dept':
                # Group by Department
                # This requires joining with Department.
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
                # Deduction breakdown
                for l in ledgers:
                    data.append({
                        "Employee": f"{l.employee.first_name}",
                        "Total Deduction": l.total_deductions,
                        "PF": l.pf_amount,
                        "ESI": l.esi_amount,
                        "Professional Tax": l.pt_amount,
                        "LOP": l.calculations_breakdown.get('lop', {}).get('amount', 0) if l.calculations_breakdown else 0
                    })
            
            elif report_type == 'tax':
                # TDS only
                for l in ledgers:
                    data.append({
                        "Employee": l.employee.first_name,
                        "PAN": l.employee.bank_details.pan_number if hasattr(l.employee, 'bank_details') else "N/A",
                        "Gross Salary": l.total_earnings,
                        "TDS Deducted": l.tds_amount
                    })

            elif report_type == 'cost':
                 # Employee Cost (CTC approach)
                 for l in ledgers:
                     # Cost = Gross + Employer PF + Employer ESI (Approximated for now)
                     # For demo, just Gross + specific overheads if any
                     data.append({
                         "Employee": l.employee.first_name,
                         "Gross Pay": l.total_earnings,
                         "Employer PF": float(l.total_earnings) * 0.12, 
                         "Employer ESI": float(l.total_earnings) * 0.0325,
                         "Total Cost": float(l.total_earnings) * 1.1525
                     })

            elif report_type == 'attendance':
                # Attendance vs Payroll
                from attendance.models import Attendance
                import calendar
                _, num_days = calendar.monthrange(month_date.year, month_date.month)
                start = month_date
                end = month_date.replace(day=num_days)
                
                for l in ledgers:
                    present = Attendance.objects.filter(
                        employee=l.employee, 
                        date__range=[start, end], 
                        status='PRESENT'
                    ).count()
                    
                    data.append({
                         "Employee": l.employee.first_name,
                         "Total Days": num_days,
                         "Present Days": present,
                         "Paid Days": num_days, 
                         "Net Pay": l.net_pay
                    })
            
            # Download handling
            export_format = request.query_params.get('format', '').lower()
            
            if export_format == 'excel':
                import pandas as pd
                import os
                from django.conf import settings
                
                df = pd.DataFrame(data)
                fname = f"report_{report_type}_{month_date}.xlsx"
                fpath = os.path.join(settings.BASE_DIR, 'media', 'reports', fname)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                df.to_excel(fpath, index=False)
                return Response({"file_url": f"/media/reports/{fname}"})

            elif export_format == 'pdf':
                from django.template.loader import get_template
                from xhtml2pdf import pisa
                from io import BytesIO
                from django.http import HttpResponse

                # Prepare context
                headers = list(data[0].keys()) if data else []
                # Convert list of dicts to list of lists for template if needed, or just iterate dicts
                # Template expects 'rows' as list of lists for strict table? or keys.
                # Let's standardize data for template: list of values
                rows = []
                for d in data:
                    rows.append(list(d.values()))
                
                context = {
                    "title": f"Report: {report_type.title()}",
                    "date": month_date,
                    "tenant": {"name": "Universal Payroll"}, # Replace with actual tenant
                    "headers": headers,
                    "data": rows,
                    "totals": [] # Calculate totals if needed
                }
                
                template = get_template('payroll/report_pdf.html')
                html = template.render(context)
                
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="report_{report_type}.pdf"'
                
                pisa_status = pisa.CreatePDF(html, dest=response)
                if pisa_status.err:
                     return Response({"error": "PDF generation error"}, status=500)
                return response

            return Response(data)
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=500)

from .models import Loan
from .serializers import LoanSerializer

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by tenant logic if needed
        # For now, if employee, see only own loans
        user = self.request.user
        if hasattr(user, 'employee'):
             return self.queryset.filter(employee=user.employee)
        return self.queryset

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

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee'):
             return self.queryset.filter(employee=user.employee)
        return self.queryset

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        r = self.get_object()
        if r.status != Reimbursement.Status.PENDING:
             return Response({"error": "Can only approve pending claims"}, status=400)
        
        r.status = Reimbursement.Status.APPROVED
        r.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
        r.save()
        return Response({"status": "Approved"})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        r = self.get_object()
        if r.status != Reimbursement.Status.PENDING:
             return Response({"error": "Can only reject pending claims"}, status=400)
        r.status = Reimbursement.Status.REJECTED
        r.save()
        return Response({"status": "Rejected"})
