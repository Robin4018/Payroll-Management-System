from decimal import Decimal
from attendance.models import Attendance
from .models import PayrollAdjustment

class BonusCalculator:
    ATTENDANCE_BONUS_AMOUNT = Decimal('1000.00')

    def __init__(self, tenant):
        self.tenant = tenant

    def calculate_monthly_bonus(self, employee, month_date):
        """
        Calculates and awards Attendance Bonus if applicable.
        Condition: Zero 'ABSENT' records in the Attendance table for this month.
        """
        import calendar
        _, num_days = calendar.monthrange(month_date.year, month_date.month)
        start_date = month_date
        end_date = month_date.replace(day=num_days)

        # 1. Cleanup old auto-generated bonuses for this month
        PayrollAdjustment.objects.filter(
            employee=employee,
            month__range=[start_date, end_date],
            type=PayrollAdjustment.Type.BONUS,
            is_auto_generated=True
        ).delete()

        # 2. Check for ANY 'ABSENT' record
        # Note: Depending on business rules, LOP/Leave logic might differ.
        # Here verification is simple: If explicit ABSENT status exists -> No bonus.
        has_absent = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date],
            status=Attendance.Status.ABSENT
        ).exists()

        if has_absent:
            print(f"DEBUG: {employee} has ABSENT records. No Attendance Bonus.")
            return

        # 3. Award Bonus
        # Optional: Check if employee was active for the full month? 
        # For MVP, assume existing active employees get it if no absent.
        
        print(f"DEBUG: Awarding Attendance Bonus to {employee}")
        
        PayrollAdjustment.objects.create(
            employee=employee,
            month=month_date,
            type=PayrollAdjustment.Type.BONUS,
            amount=self.ATTENDANCE_BONUS_AMOUNT,
            description="Auto-generated Attendance Bonus (100% Attendance)",
            is_auto_generated=True
        )
