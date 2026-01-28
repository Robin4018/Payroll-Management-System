from django.db import models
from employees.models import Employee
from tenants.models import Tenant

class SalaryComponent(models.Model):
    class ComponentType(models.TextChoices):
        EARNING = 'EARNING', 'Earning'
        DEDUCTION = 'DEDUCTION', 'Deduction'

    class CalculationType(models.TextChoices):
        FLAT = 'FLAT_AMOUNT', 'Flat Amount'
        FORMULA = 'FORMULA', 'Formula'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='salary_components')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ComponentType.choices)
    is_taxable = models.BooleanField(default=True)
    calculation_type = models.CharField(max_length=20, choices=CalculationType.choices)
    formula = models.TextField(blank=True, null=True, help_text="e.g., basic * 0.40")

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

class SalaryTemplate(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='salary_templates')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SalaryTemplateConfig(models.Model):
    template = models.ForeignKey(SalaryTemplate, on_delete=models.CASCADE, related_name='configs')
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    # Allows overriding calculation if needed, for now sticking to amount
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    formula = models.TextField(blank=True, null=True, help_text="Override component formula if needed")

    class Meta:
        unique_together = ('template', 'component')

    def __str__(self):
        return f"{self.template.name} - {self.component.name}"

class EmployeeSalaryStructure(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_structure')
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base amount for calculation")

    def __str__(self):
        return f"{self.employee} - {self.component}"

class PayrollLedger(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        HELD = 'HELD', 'Held'
        LOCKED = 'LOCKED', 'Locked' # Processed & Finalized
        PAID = 'PAID', 'Paid'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField(help_text="First day of the month")
    
    # Financials
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Statutory Breakdowns (Stored explicitly for reporting)
    pf_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    esi_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pt_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tds_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Complete Breakdown (For Payslip Generation without re-calc)
    calculations_breakdown = models.JSONField(blank=True, null=True, help_text="Full breakdown of earnings/deductions")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # Payment Tracking
    utr_number = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'month')

    def __str__(self):
        return f"{self.employee} - {self.month.strftime('%B %Y')} ({self.status})"

class PayrollAdjustment(models.Model):
    class Type(models.TextChoices):
        OVERTIME = 'OVERTIME', 'Overtime'
        ARREARS = 'ARREARS', 'Arrears'
        BONUS = 'BONUS', 'Bonus'
        INCENTIVE = 'INCENTIVE', 'Incentive'
        DEDUCTION = 'DEDUCTION', 'Adhoc Deduction'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='adjustments')
    month = models.DateField(help_text="The payroll month this applies to")
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_auto_generated = models.BooleanField(default=False, help_text="True if created by system logic (e.g. Overtime)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.type} - {self.amount}"

class Loan(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        ACTIVE = 'ACTIVE', 'Active (Repaying)'
        CLOSED = 'CLOSED', 'Closed (Fully Repaid)'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Principal Loan Amount")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Annual Interest Rate %")
    tenure_months = models.IntegerField(help_text="Number of EMIs")
    
    monthly_emi = models.DecimalField(max_digits=12, decimal_places=2, help_text="Calculated EMI")
    
    total_repaid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    reason = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_emi(self):
        """
        Simple Flat Interest or Reducing Balance?
        Let's stick to Simple Flat Interest logic for simplicity unless user asked otherwise.
        P = Principal, R = Annual Rate, N = Years.
        Interest = (P * R * (Tenure/12)) / 100
        Total = P + Interest
        EMI = Total / Tenure
        """
        if self.tenure_months <= 0: return 0
        
        principal = float(self.amount)
        rate = float(self.interest_rate)
        tenure_years = self.tenure_months / 12.0
        
        interest = (principal * rate * tenure_years) / 100.0
        total_payable = principal + interest
        emi = total_payable / self.tenure_months
        return round(emi, 2)

    def save(self, *args, **kwargs):
        if not self.monthly_emi:
            self.monthly_emi = self.calculate_emi()
        if not self.pk: # New
            self.outstanding_balance = float(self.amount) + ((float(self.amount) * float(self.interest_rate) * (self.tenure_months / 12.0)) / 100.0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"LOAN-{self.id} | {self.employee} | {self.status}"

class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payroll_ledger = models.ForeignKey(PayrollLedger, on_delete=models.SET_NULL, null=True, blank=True, related_name='loan_repayments')
    
    remarks = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.loan} - Paid {self.amount_paid}"

class Reimbursement(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved (Unpaid)'
        REJECTED = 'REJECTED', 'Rejected'
        PAID = 'PAID', 'Paid (Processed)'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reimbursements')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    title = models.CharField(max_length=255, help_text="Expense Title")
    description = models.TextField(blank=True, null=True)
    date_of_expense = models.DateField()
    
    # Attachment support (Optional for now, straightforward `FileField`)
    attachment = models.FileField(upload_to='reimbursements/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reimbursements')
    payroll_ledger = models.ForeignKey(PayrollLedger, on_delete=models.SET_NULL, null=True, blank=True, related_name='reimbursements')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.title} - {self.amount}"
