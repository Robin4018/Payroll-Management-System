from django.db import models
from employees.models import Employee
from tenants.models import Tenant

class StatutoryRate(models.Model):
    """
    Stores rates for PF, ESI, PT, etc.
    """
    class Type(models.TextChoices):
        PF = 'PF', 'Provident Fund'
        ESI = 'ESI', 'Employee State Insurance'
        PT = 'PT', 'Professional Tax'
        TDS_SLAB = 'TDS_SLAB', 'TDS Slab'

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='statutory_rates')
    type = models.CharField(max_length=20, choices=Type.choices)
    
    # Simple rate vs amount logic
    employee_contribution_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    employer_contribution_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # For limits
    wage_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Salary limit for eligibility")
    
    # For Flat amounts (like PT)
    flat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Flat amount to deduct if applicable")
    
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.effective_from}"

class TaxSlab(models.Model):
    class Regime(models.TextChoices):
        OLD = 'OLD', 'Old Regime'
        NEW = 'NEW', 'New Regime'

    regime = models.CharField(max_length=10, choices=Regime.choices)
    financial_year = models.CharField(max_length=9, help_text="e.g. 2023-2024")
    min_income = models.DecimalField(max_digits=12, decimal_places=2)
    max_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Leave blank for infinite (highest slab)")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage")
    cess_percent = models.DecimalField(max_digits=5, decimal_places=2, default=4.00)
    
    def __str__(self):
        return f"{self.regime} - {self.min_income} to {self.max_income or 'Above'} ({self.tax_rate}%)"

class TaxDeclaration(models.Model):
    """
    Employee declarations for tax savings
    """
    class Regime(models.TextChoices):
        OLD = 'OLD', 'Old Regime'
        NEW = 'NEW', 'New Regime'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tax_declarations')
    financial_year = models.CharField(max_length=9, help_text="e.g. 2023-2024")
    regime = models.CharField(max_length=10, choices=Regime.choices, default=Regime.OLD)
    
    section_80c = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="LIC, PPF, etc.")
    section_80d = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Medical Insurance")
    hra_rent_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Validation fields
    total_declared_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    verified_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_declarations')
    status = models.CharField(max_length=20, default='PENDING') # PENDING, APPROVED, LOCKED

    class Meta:
        unique_together = ('employee', 'financial_year')

    def save(self, *args, **kwargs):
        self.total_declared_amount = (self.section_80c or 0) + (self.section_80d or 0) + (self.hra_rent_paid or 0) + (self.other_deductions or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.financial_year} ({self.regime})"
