from decimal import Decimal
from .models import StatutoryRate

class ComplianceCalculator:
    def __init__(self, tenant):
        self.tenant = tenant
        # Cache rates logic could go here
    
    def calculate_pf(self, employee, basic_salary):
        """
        PF = 12% of Basic + DA.
        Rules:
        - Mandatory if Basic + DA <= 15,000.
        - If > 15,000, can restrict to 15,000 * 12% = 1800 (if unrestricted config is False).
        For this implementation: Apply 12% on Actual Basic unless capped logic introduced.
        """
        basic_salary = Decimal(str(basic_salary))
        
        pf_rate = StatutoryRate.objects.filter(tenant=self.tenant, type=StatutoryRate.Type.PF).last()
        pct = pf_rate.employee_contribution_percent if pf_rate else Decimal('12.00')
        limit = pf_rate.wage_limit if pf_rate else Decimal('15000.00')
        
        # If salary > limit, max PF = limit * 12% (1800)
        # However, many companies deduct on full basic.
        # LOGICS.txt: "Voluntary for employees earning > 15,000" -> implied full deduction usually.
        # Let's check employee preference or default to full deduction for simplicity here
        # or cap it if standard.
        # Let's stick to full deduction 12% as per most modern conventions for "EPF".
        
        pf_amount = (basic_salary * pct) / Decimal('100')
        
        # Round to nearest rupee? EPF usually rounds to nearest rupee.
        import math
        return Decimal(str(round(pf_amount)))

    def calculate_esi(self, employee, gross_salary):
        """
        ESI = 0.75% of Gross if Gross <= 21,000.
        """
        limit = Decimal('21000.00')
        gross_salary = Decimal(str(gross_salary))
        
        if gross_salary > limit:
            return Decimal('0.00')
        
        esi_rate = StatutoryRate.objects.filter(tenant=self.tenant, type=StatutoryRate.Type.ESI).last()
        pct = esi_rate.employee_contribution_percent if esi_rate else Decimal('0.75')
        
        esi_amount = (gross_salary * pct) / Decimal('100')
        
        import math
        # ESI rounds to next higher rupee
        return Decimal(str(math.ceil(esi_amount)))

    def calculate_pt(self, employee, gross_salary, month_date=None):
        """
        Professional Tax (Tamil Nadu Slabs).
        Statutory Deduction is Half-Yearly (Sept & March).
        Basis: Half-Yearly Gross Income (Projected as Monthly * 6).
        
        Slabs (Half-Yearly Gross):
        Up to 21,000 -> Nil
        21,001 - 30,000 -> 135
        30,001 - 45,000 -> 315
        45,001 - 60,000 -> 690
        60,001 - 75,000 -> 1025
        Above 75,000 -> 1250
        """
        if not month_date:
            return Decimal('0.00')

        # Only deduct in September (9) and March (3)
        if month_date.month not in [3, 9]:
            return Decimal('0.00')

        gross_salary = Decimal(str(gross_salary))
        half_yearly_gross = gross_salary * 6
        
        if half_yearly_gross <= 21000:
            return Decimal('0.00')
        elif half_yearly_gross <= 30000:
            return Decimal('135.00')
        elif half_yearly_gross <= 45000:
            return Decimal('315.00')
        elif half_yearly_gross <= 60000:
            return Decimal('690.00')
        elif half_yearly_gross <= 75000:
            return Decimal('1025.00')
        else:
            return Decimal('1250.00')

    def calculate_tds(self, employee, estimated_annual_income):
        """
        Calculates Tax Liability based on Regime and Slabs.
        Returns the MONTHLY TDS amount to be deducted.
        """
        estimated_annual_income = Decimal(str(estimated_annual_income))
        if estimated_annual_income <= 0:
            return Decimal('0.00')

        # 1. Get Declaration & Regime
        from .models import TaxDeclaration, TaxSlab
        import datetime
        
        # Financial Year Logic (Apr-Mar)
        today = datetime.date.today()
        start_year = today.year if today.month >= 4 else today.year - 1
        fy_str = f"{start_year}-{start_year+1}"
        
        declaration = TaxDeclaration.objects.filter(employee=employee, financial_year=fy_str).last()
        regime = declaration.regime if declaration else TaxDeclaration.Regime.OLD
        
        # 2. Apply Deductions
        # Standard Deduction (Flat 50k for salaried in India)
        standard_deduction = Decimal('50000.00')
        net_taxable_income = estimated_annual_income - standard_deduction
        
        if regime == TaxDeclaration.Regime.OLD:
            # Apply 80C, 80D, HRA etc.
            if declaration:
                # Use verified amount if available and "locked", else declared? 
                # For safety, let's use declared for projection, verified for final.
                deductions = declaration.section_80c + declaration.section_80d + declaration.hra_rent_paid + declaration.other_deductions
                
                # Cap 80C at 1.5L (Simplified)
                # Ideally, specific limit checks per section
                net_taxable_income -= deductions

        if net_taxable_income <= 0:
            return Decimal('0.00')

        # 3. Calculate Tax based on Slabs
        slabs = TaxSlab.objects.filter(regime=regime, financial_year=fy_str).order_by('min_income')
        
        if not slabs.exists():
             # Fallback: simple 10% flat if no slabs (or return 0)
             # return (net_taxable_income * Decimal('0.10')) / 12
             pass
             
        # Calculation Logic
        tax_total = Decimal('0.00')
        
        # Iterate Slabs
        for slab in slabs:
            if net_taxable_income > slab.min_income:
                # Determine amount in this slab
                upper_limit = slab.max_income
                lower_limit = slab.min_income
                rate = slab.tax_rate
                
                if upper_limit is None:
                    # Highest slab (e.g. > 15L)
                    taxable_amount = net_taxable_income - lower_limit
                else:
                    # Amount between min and max
                    limit_diff = upper_limit - lower_limit
                    income_above_lower = net_taxable_income - lower_limit
                    taxable_amount = min(limit_diff, income_above_lower)
                
                if taxable_amount > 0:
                    tax_in_slab = (taxable_amount * rate) / Decimal('100')
                    tax_total += tax_in_slab
                    
        # 4. Cess (4%)
        cess = (tax_total * Decimal('0.04'))
        tax_total += cess
        
        # 5. Rebate 87A (Simplified)
        if regime == TaxDeclaration.Regime.OLD and net_taxable_income <= Decimal('500000'):
             tax_total = Decimal('0.00')
        elif regime == TaxDeclaration.Regime.NEW and net_taxable_income <= Decimal('700000'):
             tax_total = Decimal('0.00')
             
        # 6. Monthly TDS
        monthly_tds = tax_total / Decimal('12')
        return round(monthly_tds, 2)
