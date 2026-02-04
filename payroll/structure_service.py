from decimal import Decimal
from payroll.models import SalaryComponent, EmployeeSalaryStructure
from employees.models import Employee

class SalaryStructureService:
    def __init__(self, tenant):
        self.tenant = tenant

    def structure_salary(self, employee, ctc_amount):
        """
        Structures the salary for an employee based on the given CTC.
        Implements logic based on standard Earnings Components:
        - Basic: 40% of CTC
        - HRA: 50% of Basic
        - DA: 0% (Configurable)
        - TA: 1600 (Fixed)
        - Medical: 1250 (Fixed)
        - Special: Balancing Component
        """
        ctc = Decimal(str(ctc_amount))
        
        # --- 1. Calculate Amounts ---
        
        # Basic Salary: 40% of CTC
        basic = ctc * Decimal('0.40')
        
        # HRA: 50% of Basic
        hra = basic * Decimal('0.50')
        
        # Dearness Allowance (DA): 0% default (Can be configured)
        da = basic * Decimal('0.00')
        
        # Fixed Allowances
        ta = Decimal('1600.00')
        medical = Decimal('1250.00')
        
        # --- Special Allowance (Balancing) ---
        # Special = CTC - (Basic + HRA + DA + TA + Medical + EmployerPF + EmployerESI)
        
        # Employer PF: 12% of (Basic + DA)
        # Note: This is an estimation for CTC breakdown purposes.
        employer_pf = (basic + da) * Decimal('0.12')
        
        # Employer ESI: 3.25% of Gross if Gross <= 21000
        # This implies a circular reference if Special is part of Gross.
        # For simple structuring of high salaries, we assume ESI is 0 or handle iteratively.
        # Let's assume 0 for initial structure unless low CTC.
        employer_esi = Decimal('0.00')
        
        # Interim Gross (Fixed parts)
        interim_gross = basic + hra + da + ta + medical
        
        # Calculate Special
        # CTC = Gross + Cost_to_Company_Components(PF, ESI)
        # CTC = (interim_gross + special) + employer_pf + employer_esi
        special = ctc - interim_gross - employer_pf - employer_esi
        
        # ESI Check for lower salaries
        # If (interim_gross + special) <= 21000, enable ESI logic
        start_gross = interim_gross + special
        if start_gross <= 21000:
             # Logic: Special = (CTC - interim - PF - 0.0325*interim) / 1.0325
             numerator = ctc - interim_gross - employer_pf - (interim_gross * Decimal('0.0325'))
             special = numerator / Decimal('1.0325')
             
             # Recalculate ESI with new special
             new_gross = interim_gross + special
             employer_esi = new_gross * Decimal('0.0325')

        if special < 0:
            special = Decimal('0.00')

        # --- 2. Define Components Map ---
        components_map = {
            'Basic Salary': {'amount': basic, 'type': 'EARNING', 'calc_type': 'FLAT_AMOUNT'},
            'House Rent Allowance': {'amount': hra, 'type': 'EARNING', 'calc_type': 'FLAT_AMOUNT'},
            'Dearness Allowance': {'amount': da, 'type': 'EARNING', 'calc_type': 'FLAT_AMOUNT'},
            'Transport Allowance': {'amount': ta, 'type': 'EARNING', 'calc_type': 'FLAT_AMOUNT'},
            'Medical Allowance': {'amount': medical, 'type': 'EARNING', 'calc_type': 'FLAT_AMOUNT'},
            'Special Allowance': {'amount': special, 'type': 'EARNING', 'calc_type': 'FLAT_AMOUNT'}
        }
        
        # --- 3. Save to DB ---
        
        # Update Employee CTC
        employee.ctc = ctc
        employee.save()
        
        # Update Structure
        for name, data in components_map.items():
            # Get or Create Component to ensure it exists
            comp, created = SalaryComponent.objects.get_or_create(
                tenant=self.tenant,
                name=name,
                defaults={
                    'type': getattr(SalaryComponent.ComponentType, data['type']),
                    'calculation_type': getattr(SalaryComponent.CalculationType, 'FLAT', 'FLAT_AMOUNT'),
                    'is_taxable': True
                }
            )
            
            # Update/Create Structure Entry
            EmployeeSalaryStructure.objects.update_or_create(
                employee=employee,
                component=comp,
                defaults={'amount': round(data['amount'], 2)}
            )
        
        # Return breakdown for UI
        return {k: round(v['amount'], 2) for k, v in components_map.items()}
