from decimal import Decimal
from payroll.models import SalaryComponent, EmployeeSalaryStructure
from employees.models import Employee

class SalaryStructureService:
    def __init__(self, tenant):
        self.tenant = tenant

    def structure_salary(self, employee, ctc_amount):
        """
        Structures the salary for an employee based on the given CTC.
        Implements logic from LOGICS.txt Section 1.
        """
        ctc = Decimal(str(ctc_amount))
        
        # 1. Provide Basic (40% of CTC)
        basic = ctc * Decimal('0.40')
        
        # 2. HRA (50% of Basic)
        hra = basic * Decimal('0.50')
        
        # 3. DA (Let's assume 0 for simplicity unless specified, 
        # LOGICS.txt says 'varies by organization'. Private usually 0 if Basic is high)
        da = Decimal('0.00') # Or basic * 0.10? Let's keep 0 to match modern structures, or make it configurable. 
        # LOGICS.txt example has DA. Let's add 0 for now.
        
        # 4. Fixed Allowances
        ta = Decimal('1600.00')
        medical = Decimal('1250.00')
        
        # Estimates for Employer Contributions to back-calculate Special
        # Employer PF = 12% of (Basic + DA) (Subject to capping, but let's assume flat 12% for CTC calculation)
        employer_pf = (basic + da) * Decimal('0.12')
        
        # Employer ESI (Complex because it depends on Gross, which depends on Special)
        # Gross = Basic + HRA + DA + TA + Medical + Special
        # If Gross <= 21000, Employer ESI = 3.25% of Gross.
        # This creates a circular dependency if Special is balancing.
        # Simplification: Assume NO ESI for structuring high salary/CTC, or iterative approach.
        # For >21k gross, ESI is 0.
        # Let's calculate interim gross without special
        interim_gross_fixed = basic + hra + da + ta + medical
        
        # Special Allowance Calculation
        # CTC = Gross + Employer Contribs
        # CTC = (interim_gross_fixed + Special) + EmployerPF + EmployerESI
        # Special = CTC - interim_gross_fixed - EmployerPF - EmployerESI
        
        # Assume ESI = 0 initially
        employer_esi = Decimal('0.00')
        
        special = ctc - interim_gross_fixed - employer_pf - employer_esi
        
        if special < 0:
            special = Decimal('0.00') 
            # If negative, we might need to reduce Basic or HRA to fit. 
            # For now, let's clamp to 0.
            
        # Re-check ESI applicability
        gross = interim_gross_fixed + special
        if gross <= 21000:
            employer_esi = gross * Decimal('0.0325')
            # Recalculate Special with ESI?
            # Special = CTC - interim - PF - (0.0325 * (interim + Special))
            # Special = CTC - interim - PF - 0.0325*interim - 0.0325*Special
            # Special * (1.0325) = CTC - interim - PF - 0.0325*interim
            # Special = (CTC - interim - PF - 0.0325*interim) / 1.0325
            
            numerator = ctc - interim_gross_fixed - employer_pf - (interim_gross_fixed * Decimal('0.0325'))
            special = numerator / Decimal('1.0325')
            if special < 0: special = 0
            
            # Recalculate Gross and ESI
            gross = interim_gross_fixed + special
            employer_esi = gross * Decimal('0.0325')

        # Final breakdown dictionary
        components_map = {
            'Basic Salary': basic,
            'House Rent Allowance': hra,
            'Dearness Allowance': da,
            'Transport Allowance': ta,
            'Medical Allowance': medical,
            'Special Allowance': special
        }
        
        # Save to DB
        # Update Employee CTC
        employee.ctc = ctc
        employee.save()
        
        # Create/Update EmployeeSalaryStructure
        # 1. Clear existing generic structure if we are strictly re-structuring
        # Or better, update_or_create by component.
        
        for name, amount in components_map.items():
            comp = SalaryComponent.objects.filter(tenant=self.tenant, name=name).first()
            if comp:
                EmployeeSalaryStructure.objects.update_or_create(
                    employee=employee,
                    component=comp,
                    defaults={'amount': round(amount, 2)}
                )
        
        return components_map
