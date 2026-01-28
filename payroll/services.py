from decimal import Decimal
from datetime import date
from .models import SalaryComponent, EmployeeSalaryStructure, PayrollLedger
from employees.models import Employee

from .services_ot import OvertimeCalculator
from .services_bonus import BonusCalculator

class PayrollCalculator:
    def __init__(self, tenant):
        self.tenant = tenant

    def calculate_employee_salary(self, employee, month_date):
        """
        Calculates salary for a single employee for a specific month.
        """
        # 0. Auto-Calculate Overtime & Bonus
        try:
            ot_calc = OvertimeCalculator(self.tenant)
            ot_calc.calculate_monthly_overtime(employee, month_date)
            
            bonus_calc = BonusCalculator(self.tenant)
            bonus_calc.calculate_monthly_bonus(employee, month_date)
        except Exception as e:
            print(f"Error calculating OT/Bonus for {employee}: {e}")

        salary_structure = EmployeeSalaryStructure.objects.filter(employee=employee)
        
        earnings_total = Decimal('0.00')
        deductions_total = Decimal('0.00')
        
        # 1. Calculate Earnings
        base_components = {} # Store flat amounts for formula reference if needed (e.g. Basic)
        
        # First pass: Flat Amounts
        for item in salary_structure:
            print(f"DEBUG: Processing {item.component.name} type={item.component.calculation_type}")
            if str(item.component.calculation_type) == 'FLAT_AMOUNT':
                amount = item.amount
                base_components[item.component.name.lower()] = amount
                
                if item.component.type == SalaryComponent.ComponentType.EARNING:
                    earnings_total += amount
                else:
                    deductions_total += amount

        # Second pass: Formulas (Simple implementation)
        # Note: In a real system, you'd need a robust parser or dependency graph. 
        # Here we assume formulas only reference "basic" or other flat components.
        for item in salary_structure:
            if str(item.component.calculation_type) == 'FORMULA':
                formula = item.component.formula
                # Simple evaluation: replace 'basic' with value
                # WARNING: eval is dangerous. In production, use a safe mathemetical parser.
                # For this demo, we assume the formula is trusted admin input.
                
                # Context for eval
                context = base_components.copy()
                
                try:
                    # Replace variable names in formula? 
                    # Actually, let's just use eval with the context dictionary.
                    # e.g. "basic * 0.40" -> basic must be in context.
                    res = eval(formula, {}, context)
                    amount = Decimal(str(res))
                    print(f"DEBUG: Success {item.component.name}: {formula} -> {amount}")
                except Exception as e:
                    print(f"DEBUG: Error calculating formula {formula} for {employee}: {e}")
                    print(f"DEBUG: Context was: {context}")
                    amount = Decimal('0.00')

                if item.component.type == SalaryComponent.ComponentType.EARNING:
                    earnings_total += amount
                else:
                    # Check if this is a Statutory Component and recalculate if needed?
                    # For now, we will ADD specific Statutory deductions separately below if they aren't explicit components,
                    # OR we define them here.
                    # APPROACH: Let's assume the user has Basic, HRA etc. in structure.
                    # We will Auto-Calculate PF/ESI/PT/TDS and append/overwrite.
                    deductions_total += amount

        # 2.5 Calculate Adjustments (OT, Bonus, Arrears)
        from .models import PayrollAdjustment
        
        # We need to find adjustments for this specific month
        # Assuming month_date is the 1st of the month
        import calendar
        _, num_days = calendar.monthrange(month_date.year, month_date.month)
        start_date = month_date
        end_date = month_date.replace(day=num_days)

        adjustments = PayrollAdjustment.objects.filter(
            employee=employee,
            month__range=[start_date, end_date]
        )
        
        adjustment_earnings = Decimal('0.00')
        adjustment_deductions = Decimal('0.00')

        for adj in adjustments:
            print(f"DEBUG: Adjustment {adj.type} -> {adj.amount}")
            if adj.type == PayrollAdjustment.Type.DEDUCTION:
                adjustment_deductions += adj.amount
                deductions_total += adj.amount
            else:
                adjustment_earnings += adj.amount
                earnings_total += adj.amount

        # 3. Calculate Loss of Pay (LOP) & Proration
        from attendance.models import Attendance, LeaveRequest
        import calendar
        
        # Standard Working Days as per LOGICS.txt (26 days default)
        STANDARD_WORKING_DAYS = Decimal('26.00')
        
        # Get total days in the month
        _, num_days_in_month = calendar.monthrange(month_date.year, month_date.month)
        
        # -- A. Proration for New Joiners --
        # If joined this month, we pay only for days joined.
        # Logic 15B: Prorate = (Monthly_Gross / Working_Days) * Days_Worked
        # Wait, if we use LOP deduction method:
        # Prorated Days = Total Days - Dates Before Joining
        # LOP Days = Actual Absent + Dates Before Joining
        
        effective_start_date = month_date
        effective_end_date = month_date.replace(day=num_days_in_month)
        
        proration_lop_days = 0
        
        if employee.date_of_joining > effective_start_date:
             # Employee joined mid-month
             effective_start_date = employee.date_of_joining
             # Days before joining are effectively LOP (or just not payable)
             # But if we use Working Days denominator, we should maintain consistency.
             # Approach: Calculate "Payable Days" directly?
             # LOGICS.txt: Proportionate_Salary = (Monthly_Gross / Working_Days) * Days_Worked
             
             # Let's count days in month NOT worked due to joining late
             # This is complex with "Working Days" (26) vs "Calendar Days".
             # Simple approaches:
             # 1. Calculate Per Day Salary = Gross / 26
             # 2. Calculate Payable Days = (Days in Month - Days Before Joining) -> normalized to working days?
             
             # Let's stick to LOP deduction method for simplicity and consistency.
             # Any day before DOJ is a "Zero Pay Day".
             # But does it count as "Absent"?
             pass

        # Find Absent days in the effective range
        # We assume month_date is the 1st of the month
        
        start_date = month_date
        end_date = month_date.replace(day=num_days_in_month)
        
        absent_days = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date],
            status=Attendance.Status.ABSENT
        )
        
        lop_days = 0
        for attendance in absent_days:
            # Check if covered by PAID Leave
            is_covered = LeaveRequest.objects.filter(
                employee=employee,
                status=LeaveRequest.Status.APPROVED,
                leave_type__is_paid=True,
                start_date__lte=attendance.date,
                end_date__gte=attendance.date
            ).exists()
            
            if not is_covered:
                lop_days += 1

        # Check Proration (Mid-month Joining)
        # If joined on 15th, Days 1-14 are not "Absent" in attendance table, but are unpaid.
        # We need to add them to "Unpaid Days" or calculate "Payable Days".
        
        payable_days = STANDARD_WORKING_DAYS # Default 26
        
        if employee.date_of_joining > start_date:
            # Joined Late
            # Days active in month
            days_active = (end_date - employee.date_of_joining).days + 1
            if days_active < 0: days_active = 0
            
            # Convert active calendar days to pro-rated working days?
            # Ratio: days_active / num_days_in_month
            # Prorated Working Days = 26 * Ratio
            ratio = Decimal(days_active) / Decimal(num_days_in_month)
            payable_days = STANDARD_WORKING_DAYS * ratio
        
        # Now deduct LOP from Payable Days
        # Wait, LOP is strictly absent days from 'payable' period.
        
        # REVISED APPROACH based on LOGICS.txt "Proportionate Salary":
        # Proportionate = (Monthly / 26) * Days_Worked
        # Days_Worked = Payable_Days_Base - Absent_Days
        
        final_payable_days = payable_days - Decimal(lop_days)
        if final_payable_days < 0: final_payable_days = 0
        
        # Calculate Deduction Logic:
        # Deduction = (Monthly / 26) * (26 - Final_Payable)
        # This covers both Proration (Not joined) and LOP (Absent)
        
        lop_units = STANDARD_WORKING_DAYS - final_payable_days
        
        lop_deduction = Decimal('0.00')
        if earnings_total > 0:
            daily_salary = earnings_total / STANDARD_WORKING_DAYS
            lop_deduction = daily_salary * lop_units
            lop_deduction = round(lop_deduction, 2)
            
            if lop_units > 0:
                print(f"DEBUG: LOP/Proration for {employee}: {lop_units:.2f} units -> {lop_deduction}")
                deductions_total += lop_deduction
        
        # Store for reporting
        lop_days_count = lop_days # Actual absent
        # We might want to store 'unpaid_days' (absent + pre-joining)

        
        # 4. STATUTORY COMPLIANCE (The integration)
        # We calculate this on the "Earned Gross" (Earnings - LOP)
        earned_gross = earnings_total - lop_deduction
        
        # PF Basis = Basic + DA
        basic_salary = base_components.get('basic salary', Decimal('0.00')) 
        da_amount = base_components.get('dearness allowance', Decimal('0.00'))
        pf_basis = basic_salary + da_amount
        
        from compliance.services import ComplianceCalculator
        comp_calc = ComplianceCalculator(self.tenant)
        
        
        pf_amt = comp_calc.calculate_pf(employee, pf_basis)
        esi_amt = comp_calc.calculate_esi(employee, earned_gross)
        pt_amt = comp_calc.calculate_pt(employee, earned_gross, month_date=month_date)
        tds_amt = comp_calc.calculate_tds(employee, earned_gross * 12) 
        
        statutory_deductions = pf_amt + esi_amt + pt_amt + tds_amt
        deductions_total += statutory_deductions
        
        # --- LOAN DEDUCTION ---
        from .models import Loan
        active_loans = Loan.objects.filter(employee=employee, status=Loan.Status.ACTIVE)
        total_emi = Decimal('0.00')
        loans_breakdown = []
        
        for loan in active_loans:
            emi = loan.monthly_emi
            # Check if loan closed? No, status is active.
            # Adjust if outstanding < emi
            if loan.outstanding_balance < emi:
                emi = loan.outstanding_balance
            
            total_emi += emi
            loans_breakdown.append({'loan_id': loan.id, 'amount': float(emi)})
            
        deductions_total += total_emi
        # ----------------------
        
        # --- REIMBURSEMENTS ---
        from .models import Reimbursement
        approved_reimbursements = Reimbursement.objects.filter(employee=employee, status=Reimbursement.Status.APPROVED, payroll_ledger__isnull=True)
        reimbursement_total = Decimal('0.00')
        reimbursement_details = []
        
        for r in approved_reimbursements:
             reimbursement_total += r.amount
             reimbursement_details.append({'id': r.id, 'title': r.title, 'amount': float(r.amount)})
             
        earnings_total += reimbursement_total
        # ----------------------
        
        net_pay = earnings_total - deductions_total

        # Construct Breakdown JSON
        breakdown = {
            "earnings": {k: float(v) for k, v in base_components.items()},
            "formula_earnings": {}, # Could track separately if needed
            "adjustments": {
                "additions": float(adjustment_earnings),
                "deductions": float(adjustment_deductions)
            },
            "statutory": {
                "pf": float(pf_amt),
                "esi": float(esi_amt),
                "pt": float(pt_amt),
                "tds": float(tds_amt)
            },
            "loans": {
                "total": float(total_emi),
                "details": loans_breakdown
            },
            "reimbursements": {
                "total": float(reimbursement_total),
                "details": reimbursement_details
            },
            "lop": {
                "days": float(lop_units),
                "amount": float(lop_deduction)
            }
        }

        # Create/Update Ledger
        ledger, created = PayrollLedger.objects.update_or_create(
            employee=employee,
            month=month_date,
            defaults={
                'total_earnings': earnings_total,
                'total_deductions': deductions_total,
                'net_pay': net_pay,
                'pf_amount': pf_amt,
                'esi_amount': esi_amt,
                'pt_amount': pt_amt,
                'tds_amount': tds_amt,
                'calculations_breakdown': breakdown,
                'status': PayrollLedger.Status.DRAFT
            }
        )
        return ledger

    def run_payroll_for_tenant(self, month_date, employee_list=None):
        """
        Runs payroll for a tenant. 
        Args:
            month_date: Date object (1st of month)
            employee_list: Optional queryset or list of IDs to process specifically.
        """
        if employee_list:
            # If list of IDs provided
            if isinstance(employee_list[0], int) or isinstance(employee_list[0], str):
                employees = Employee.objects.filter(id__in=employee_list, tenant=self.tenant)
            else:
                employees = employee_list
        else:
            employees = Employee.objects.filter(tenant=self.tenant, is_active=True)
            
        results = []
        for emp in employees:
            try:
                ledger = self.calculate_employee_salary(emp, month_date)
                results.append(ledger)
            except Exception as e:
                print(f"Error processing payroll for {emp}: {e}")
                # Ideally log error explicitly or return error struct
        return results
