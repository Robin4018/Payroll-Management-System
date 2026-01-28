from decimal import Decimal
from datetime import timedelta
import math
from attendance.models import Attendance
from .models import PayrollAdjustment, EmployeeSalaryStructure, SalaryComponent

class OvertimeCalculator:
    WORKING_HOURS_THRESHOLD = 9
    OVERTIME_RATE_MULTIPLIER = 1.5
    WORKING_DAYS_MONTH = Decimal('26.0')
    HOURS_PER_DAY = Decimal('8.0')

    def __init__(self, tenant):
        self.tenant = tenant

    def calculate_monthly_overtime(self, employee, month_date):
        """
        Calculates and creates Overtime adjustments for the given month.
        Idempotency: Deletes existing auto-generated OT adjustments for this month first.
        """
        import calendar
        _, num_days = calendar.monthrange(month_date.year, month_date.month)
        start_date = month_date
        end_date = month_date.replace(day=num_days)

        # 1. Cleanup old auto-generated records for this month to prevent duplicates
        PayrollAdjustment.objects.filter(
            employee=employee,
            month__range=[start_date, end_date],
            type=PayrollAdjustment.Type.OVERTIME,
            is_auto_generated=True
        ).delete()

        # 2. Get Attendance
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date],
            status=Attendance.Status.PRESENT,
            check_in__isnull=False,
            check_out__isnull=False
        )

        total_ot_hours = 0.0

        for record in attendance_records:
            # Calculate duration
            # Convert time to datetime for diff
            # Note: This naively assumes check-in/out are on same day. 
            # If shift spans midnight, this logic needs improvement (using datetime combining date+time).
            # For this MVP, we assume single day shift.
            
            # Combine Date + Time
            try:
                # We need to use datetime.datetime.combine approach
                from datetime import datetime
                cin = datetime.combine(record.date, record.check_in)
                cout = datetime.combine(record.date, record.check_out)
                
                if cout < cin:
                     # Shift spanned midnight? Or error?
                     # Let's ignore for now or add 1 day? 
                     # Skipping complex midnight logic for MVP unless requested.
                     continue

                duration = (cout - cin).total_seconds() / 3600.0 # Hours
                
                if duration > self.WORKING_HOURS_THRESHOLD:
                    ot_hours = duration - self.WORKING_HOURS_THRESHOLD
                    total_ot_hours += ot_hours
                    print(f"DEBUG: OT for {employee} on {record.date}: {duration:.2f} hrs worked, {ot_hours:.2f} hrs OT")
            except Exception as e:
                print(f"Error calculating OT for {record}: {e}")

        if total_ot_hours <= 0:
            return

        # 3. Calculate Rate
        # Formula: (Basic + DA) / 26 / 8 * 1.5
        structure = EmployeeSalaryStructure.objects.filter(employee=employee)
        base_salary = Decimal('0.00')
        
        for item in structure:
            name_lower = item.component.name.lower()
            if 'basic' in name_lower or 'dearness' in name_lower or 'da' in name_lower:
                if str(item.component.calculation_type) == 'FLAT_AMOUNT':
                    base_salary += item.amount
                # If formula, we skip complex parsing here for simplicity or need to re-eval.
                # Assuming Basic is usually Flat.
        
        if base_salary == 0:
            # Fallback to some default or skip?
            print(f"Warning: No Basic/DA found for {employee}, skipping OT calc")
            return

        hourly_rate = (base_salary / self.WORKING_DAYS_MONTH / self.HOURS_PER_DAY)
        ot_rate = hourly_rate * Decimal(str(self.OVERTIME_RATE_MULTIPLIER))
        
        total_ot_amount = ot_rate * Decimal(str(total_ot_hours))
        total_ot_amount = round(total_ot_amount, 2)
        
        print(f"DEBUG: Total OT for {employee}: {total_ot_hours:.2f} hrs @ {ot_rate:.2f}/hr = {total_ot_amount}")

        # 4. Create Adjustment
        PayrollAdjustment.objects.create(
            employee=employee,
            month=month_date, # Or logic to map to exact pay period
            type=PayrollAdjustment.Type.OVERTIME,
            amount=total_ot_amount,
            description=f"Auto-calculated Overtime: {total_ot_hours:.2f} hours @ 1.5x rate",
            is_auto_generated=True
        )
