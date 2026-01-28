import os
import django
import sys
from collections import defaultdict

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') 
django.setup()

from employees.models import Employee

def run():
    print("Starting Duplicate Merge...")
    
    # Group by name
    employees_by_name = defaultdict(list)
    all_employees = Employee.objects.all().order_by('id')
    
    for emp in all_employees:
        # Normalize name check
        key = emp.first_name.strip().lower()
        employees_by_name[key].append(emp)
        
    merged_count = 0
    
    for name_key, emp_list in employees_by_name.items():
        if len(emp_list) > 1:
            print(f"Found duplicates for: {emp_list[0].first_name} ({len(emp_list)} records)")
            
            # Keep the primary one (first created / lowest ID)
            primary_emp = emp_list[0]
            duplicates = emp_list[1:]
            
            # Departments to add
            secondary_depts = []
            
            for dup in duplicates:
                if dup.department and dup.department != primary_emp.department:
                    secondary_depts.append(dup.department)
                    print(f"  - Merging department: {dup.department.name}")
                
                # Check for other fields to merge? 
                # Assuming qualification/designation are similar or primary is correct.
                # If designations differ, we might want to capture that? 
                # User said "mention their departments".
                # We could append designation to the primary if distinct? 
                # "Assistant Professor (Commerce)" vs "Assistant Professor (Commerce with CA)"
                # Let's keep primary designation but ensure secondary depts are linked.
            
            # Add secondary departments to primary
            if secondary_depts:
                # Need to use set to avoid dupes in M2M adding? .add() handles it.
                for dept in secondary_depts:
                    primary_emp.secondary_departments.add(dept)
            
            # Save primary to ensure M2M persistence? .add() saves immediately.
            
            # Delete duplicates
            for dup in duplicates:
                print(f"  - Deleting duplicate ID: {dup.employee_code}")
                dup.delete()
            
            merged_count += 1

    print(f"Migration Complete. Merged {merged_count} sets of duplicates.")
    print(f"Total Employees Remaining: {Employee.objects.count()}")

if __name__ == '__main__':
    run()
